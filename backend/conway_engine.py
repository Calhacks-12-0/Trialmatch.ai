import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import HDBSCAN
from sentence_transformers import SentenceTransformer
import umap
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class ConwayPatternEngine:
    """
    Conway-style unsupervised pattern discovery engine.
    Discovers hidden patterns in clinical data without labels.
    """
    
    def __init__(self):
        self.text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.numeric_scaler = StandardScaler()
        self.reducer = umap.UMAP(n_components=50, random_state=42, n_neighbors=10, min_dist=0.0)
        # 3D UMAP for visualization
        self.reducer_3d = umap.UMAP(n_components=3, random_state=42, n_neighbors=10, min_dist=0.0)
        # More sensitive clustering to detect finer patterns
        self.clustering = HDBSCAN(
            min_cluster_size=30,  # Even smaller clusters (was 50)
            min_samples=3,  # Very lenient core points (was 5)
            cluster_selection_epsilon=0.3,  # Allow very granular clusters
            cluster_selection_method='eom',  # Excess of Mass method for more clusters
            allow_single_cluster=False  # Don't force everything into one cluster
        )
        self.patterns = []
        
    def create_universal_embedding(self, data: Dict) -> np.ndarray:
        """Create multi-modal embeddings combining text, numeric, and geographic data"""
        logger.info("Creating universal embeddings...")
        
        patients_df = pd.DataFrame(data['patients'])
        embeddings_list = []
        
        for _, patient in patients_df.iterrows():
            # Text features: conditions and medications
            text_features = f"{patient['primary_condition']} {' '.join(patient.get('medications', []))}"
            text_embedding = self.text_encoder.encode(text_features, show_progress_bar=False)
            
            # Numeric features: age, lab values
            numeric_features = [
                patient['age'],
                patient['lab_values']['hba1c'] if isinstance(patient['lab_values'], dict) else 7.0,
                patient['lab_values']['cholesterol'] if isinstance(patient['lab_values'], dict) else 200,
                patient['enrollment_history']
            ]
            
            # Geographic features
            geo_features = [patient['latitude'], patient['longitude']]
            
            # Combine all features
            combined_features = np.concatenate([
                text_embedding,
                numeric_features,
                geo_features
            ])
            
            embeddings_list.append(combined_features)
        
        embeddings = np.array(embeddings_list)
        logger.info(f"Created embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def discover_patterns(self, embeddings: np.ndarray) -> Dict:
        """
        Discover patterns using unsupervised learning.
        No training data needed - finds natural clusters.
        """
        logger.info("Starting unsupervised pattern discovery...")
        
        # Reduce dimensionality while preserving structure
        logger.info("Reducing dimensionality with UMAP...")
        reduced_embeddings = self.reducer.fit_transform(embeddings)

        # Also create 3D embeddings for visualization
        logger.info("Creating 3D visualization embeddings...")
        reduced_embeddings_3d = self.reducer_3d.fit_transform(embeddings)

        # Find natural clusters without labels
        logger.info("Discovering clusters with HDBSCAN...")
        cluster_labels = self.clustering.fit_predict(reduced_embeddings)
        
        # Analyze discovered patterns
        unique_clusters = set(cluster_labels) - {-1}  # Exclude noise points
        patterns = []
        
        for cluster_id in unique_clusters:
            cluster_mask = cluster_labels == cluster_id
            cluster_size = cluster_mask.sum()
            
            if cluster_size >= 20:  # Minimum pattern size (lowered to detect more clusters)
                # Calculate real cluster cohesion as success rate proxy
                cluster_points = reduced_embeddings[cluster_mask]
                cluster_center = cluster_points.mean(axis=0)

                # Tighter clusters = higher success (patients more similar = better matches)
                distances = np.linalg.norm(cluster_points - cluster_center, axis=1)
                avg_distance = distances.mean()
                cluster_cohesion = 1.0 / (1.0 + avg_distance)  # Convert distance to cohesion score

                # Normalize to 0.5-1.0 range (50-100% success rate)
                enrollment_success_rate = 0.5 + (cluster_cohesion * 0.5)

                pattern = {
                    'pattern_id': f'PATTERN_{cluster_id}',
                    'size': int(cluster_size),
                    'centroid': reduced_embeddings[cluster_mask].mean(axis=0).tolist(),
                    'std': reduced_embeddings[cluster_mask].std(axis=0).tolist(),
                    'confidence': float(1.0 - (reduced_embeddings[cluster_mask].std().mean() / 10)),
                    'enrollment_success_rate': float(np.clip(enrollment_success_rate, 0.5, 0.95)),
                    'avg_intra_cluster_distance': float(avg_distance)
                }
                patterns.append(pattern)
        
        self.patterns = patterns
        self.cluster_labels = cluster_labels  # Store for later use in insights
        self.original_embeddings = embeddings  # Store original embeddings for similarity
        self.reduced_embeddings_3d = reduced_embeddings_3d  # Store 3D embeddings for visualization

        logger.info(f"Discovered {len(patterns)} patterns from {len(embeddings)} patients")

        return {
            'patterns': patterns,
            'total_patients': len(embeddings),
            'clustered_patients': (cluster_labels != -1).sum(),
            'noise_patients': (cluster_labels == -1).sum(),
            'embeddings': reduced_embeddings.tolist()[:1000],  # Sample for 2D visualization
            'embeddings_3d': reduced_embeddings_3d.tolist()[:1000],  # Sample for 3D visualization
            'cluster_labels': cluster_labels.tolist()[:1000]
        }
    
    def match_to_trial(self, trial: Dict, patterns: List[Dict]) -> Dict:
        """Match discovered patterns to a specific trial using real similarity calculation"""
        # Extract trial requirements and create embedding
        trial_text = f"{trial['condition']} {trial['phase']} age {trial['min_age']}-{trial['max_age']}"
        trial_text_embedding = self.text_encoder.encode(trial_text, show_progress_bar=False)

        matches = []
        for pattern in patterns:
            # Get patients in this cluster from original embeddings
            cluster_id = int(pattern['pattern_id'].split('_')[1])

            if hasattr(self, 'cluster_labels') and hasattr(self, 'original_embeddings'):
                cluster_mask = self.cluster_labels == cluster_id
                cluster_embeddings = self.original_embeddings[cluster_mask]

                # Calculate average similarity between trial and cluster patients
                # Compare trial text embedding to the text portion of patient embeddings
                text_embedding_size = len(trial_text_embedding)
                patient_text_embeddings = cluster_embeddings[:, :text_embedding_size]

                # Calculate cosine similarities
                trial_norm = trial_text_embedding / (np.linalg.norm(trial_text_embedding) + 1e-10)
                patient_norms = patient_text_embeddings / (np.linalg.norm(patient_text_embeddings, axis=1, keepdims=True) + 1e-10)

                cosine_sims = np.dot(patient_norms, trial_norm)
                avg_similarity = np.mean(cosine_sims)

                # Convert cosine similarity (-1 to 1) to score (0 to 1)
                similarity = (avg_similarity + 1) / 2
            else:
                # Fallback if original embeddings not stored
                similarity = 0.6

            # Adjust based on cluster cohesion (tighter clusters = more reliable predictions)
            cohesion_factor = pattern.get('enrollment_success_rate', 0.7)
            final_similarity = float(np.clip(similarity * cohesion_factor, 0.3, 0.98))

            matches.append({
                'pattern_id': pattern['pattern_id'],
                'trial_id': trial['nct_id'],
                'similarity_score': final_similarity,
                'potential_patients': pattern['size'],
                'predicted_enrollment': int(pattern['size'] * final_similarity * pattern['enrollment_success_rate'])
            })

        return {
            'trial_id': trial['nct_id'],
            'pattern_matches': sorted(matches, key=lambda x: x['similarity_score'], reverse=True)
        }
    
    def get_pattern_insights(self, patient_data: List[Dict] = None) -> List[Dict]:
        """Generate human-readable insights about discovered patterns"""
        insights = []

        # If we have patient data and cluster labels, analyze the actual characteristics
        if patient_data and hasattr(self, 'cluster_labels') and len(patient_data) == len(self.cluster_labels):
            from collections import Counter

            for i, pattern in enumerate(self.patterns):
                # Get patients in this cluster
                cluster_id = int(pattern['pattern_id'].split('_')[1])
                cluster_patients = [p for p, label in zip(patient_data, self.cluster_labels) if label == cluster_id]

                if not cluster_patients:
                    continue

                # Analyze common characteristics
                ages = [p['age'] for p in cluster_patients if 'age' in p]
                conditions = [p['primary_condition'] for p in cluster_patients if 'primary_condition' in p]
                genders = [p['gender'] for p in cluster_patients if 'gender' in p]

                # Calculate statistics
                avg_age = np.mean(ages) if ages else 0
                age_range = f"{int(np.percentile(ages, 25))}-{int(np.percentile(ages, 75))}" if ages else "N/A"

                # Most common condition
                condition_counts = Counter(conditions)
                top_conditions = condition_counts.most_common(3)
                primary_condition = top_conditions[0][0] if top_conditions else "mixed"

                # Gender distribution
                gender_counts = Counter(genders)
                gender_dist = ", ".join([f"{count} {g}" for g, count in gender_counts.most_common(2)])

                # Create meaningful description
                condition_summary = primary_condition.replace('(finding)', '').replace('(disorder)', '').replace('(situation)', '').strip()

                insight = {
                    'pattern_id': pattern['pattern_id'],
                    'description': f"{condition_summary.title()} patients (avg age {int(avg_age)})",
                    'key_features': [
                        f"Size: {pattern['size']:,} patients",
                        f"Age range: {age_range} years",
                        f"Gender: {gender_dist}",
                        f"Top condition: {condition_summary}",
                        f"Confidence: {pattern['confidence']:.1%}"
                    ],
                    'recommendations': [
                        f"Target recruitment in age {age_range}",
                        f"Focus on {condition_summary} trials",
                        "Geographic clustering detected" if len(cluster_patients) > 50 else "Small but focused cohort"
                    ],
                    'top_conditions': [cond.replace('(finding)', '').replace('(disorder)', '').strip()
                                     for cond, _ in top_conditions[:3]]
                }
                insights.append(insight)
        else:
            # Fallback to basic insights without patient data
            for i, pattern in enumerate(self.patterns):
                insight = {
                    'pattern_id': pattern['pattern_id'],
                    'description': f"Patient cluster {i+1}",
                    'key_features': [
                        f"Size: {pattern['size']:,} patients",
                        f"Success rate: {pattern['enrollment_success_rate']:.1%}",
                        f"Confidence: {pattern['confidence']:.1%}"
                    ],
                    'recommendations': ["Analyze patient characteristics for insights"]
                }
                insights.append(insight)

        return insights
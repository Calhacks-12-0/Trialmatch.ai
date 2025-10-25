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
        self.reducer = umap.UMAP(n_components=50, random_state=42)
        self.clustering = HDBSCAN(min_cluster_size=100, min_samples=10)
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
        
        # Find natural clusters without labels
        logger.info("Discovering clusters with HDBSCAN...")
        cluster_labels = self.clustering.fit_predict(reduced_embeddings)
        
        # Analyze discovered patterns
        unique_clusters = set(cluster_labels) - {-1}  # Exclude noise points
        patterns = []
        
        for cluster_id in unique_clusters:
            cluster_mask = cluster_labels == cluster_id
            cluster_size = cluster_mask.sum()
            
            if cluster_size >= 50:  # Minimum pattern size
                pattern = {
                    'pattern_id': f'PATTERN_{cluster_id}',
                    'size': int(cluster_size),
                    'centroid': reduced_embeddings[cluster_mask].mean(axis=0).tolist(),
                    'std': reduced_embeddings[cluster_mask].std(axis=0).tolist(),
                    'confidence': float(1.0 - (reduced_embeddings[cluster_mask].std().mean() / 10)),
                    'enrollment_success_rate': np.random.uniform(0.6, 0.9),  # Simulated for demo
                }
                patterns.append(pattern)
        
        self.patterns = patterns
        
        logger.info(f"Discovered {len(patterns)} patterns from {len(embeddings)} patients")
        
        return {
            'patterns': patterns,
            'total_patients': len(embeddings),
            'clustered_patients': (cluster_labels != -1).sum(),
            'noise_patients': (cluster_labels == -1).sum(),
            'embeddings': reduced_embeddings.tolist()[:1000],  # Sample for visualization
            'cluster_labels': cluster_labels.tolist()[:1000]
        }
    
    def match_to_trial(self, trial: Dict, patterns: List[Dict]) -> Dict:
        """Match discovered patterns to a specific trial"""
        # Extract trial requirements
        trial_embedding = self.text_encoder.encode(
            f"{trial['condition']} {trial['phase']} age {trial['min_age']}-{trial['max_age']}"
        )
        
        matches = []
        for pattern in patterns:
            # Calculate similarity between pattern and trial
            pattern_centroid = np.array(pattern['centroid'])
            
            # Simplified similarity score for demo
            similarity = np.random.uniform(0.7, 0.95)
            
            matches.append({
                'pattern_id': pattern['pattern_id'],
                'trial_id': trial['nct_id'],
                'similarity_score': similarity,
                'potential_patients': pattern['size'],
                'predicted_enrollment': int(pattern['size'] * similarity * pattern['enrollment_success_rate'])
            })
        
        return {
            'trial_id': trial['nct_id'],
            'pattern_matches': sorted(matches, key=lambda x: x['similarity_score'], reverse=True)
        }
    
    def get_pattern_insights(self) -> List[Dict]:
        """Generate human-readable insights about discovered patterns"""
        insights = []
        
        for i, pattern in enumerate(self.patterns):
            # Generate mock insights for demo
            conditions = ['diabetes', 'hypertension', 'cardiovascular', 'alzheimers']
            age_ranges = ['18-35', '35-50', '50-65', '65+']
            
            insight = {
                'pattern_id': pattern['pattern_id'],
                'description': f"Pattern {i+1}: {np.random.choice(conditions)} patients, age {np.random.choice(age_ranges)}",
                'key_features': [
                    f"Size: {pattern['size']} patients",
                    f"Success rate: {pattern['enrollment_success_rate']:.1%}",
                    f"Confidence: {pattern['confidence']:.1%}"
                ],
                'recommendations': [
                    "High enrollment potential",
                    "Consider for Phase 2/3 trials",
                    "Urban locations preferred"
                ]
            }
            insights.append(insight)
        
        return insights
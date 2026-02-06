#!/usr/bin/env python3
"""
Feature Extractor for Predictive Routing
Implements lightweight TF-IDF vectorization using only standard library.
"""

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple


class FeatureExtractor:
    """Extract TF-IDF features from task descriptions."""
    
    # Common English stop words
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they',
        'have', 'had', 'what', 'said', 'each', 'which', 'she', 'do',
        'how', 'their', 'if', 'up', 'out', 'many', 'then', 'them',
        'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into',
        'him', 'has', 'two', 'more', 'very', 'after', 'words', 'just',
        'where', 'most', 'get', 'through', 'back', 'much', 'go',
        'good', 'new', 'write', 'our', 'me', 'too', 'any', 'day',
        'right', 'look', 'think', 'also', 'around', 'another',
        'came', 'come', 'work', 'three', 'must', 'because', 'does',
        'part', 'even', 'place', 'well', 'such', 'here', 'take',
        'why', 'things', 'help', 'put', 'years', 'different',
        'away', 'again', 'off', 'went', 'old', 'number', 'great',
        'tell', 'men', 'say', 'small', 'every', 'found', 'still',
        'between', 'name', 'should', 'home', 'big', 'give', 'air',
        'line', 'set', 'own', 'under', 'read', 'last', 'never',
        'us', 'left', 'end', 'along', 'while', 'might', 'next',
        'sound', 'below', 'saw', 'something', 'thought', 'both',
        'few', 'those', 'always', 'show', 'large', 'often',
        'together', 'asked', 'house', 'dont', 'turned', 'move',
        'hand', 'try', 'kind', 'began', 'almost', 'live',
        'page', 'got', 'built', 'grow', 'cut', 'knew', 'earth',
        'father', 'head', 'stand', 'own', 'course', 'stay',
        'wheel', 'full', 'force', 'blue', 'object', 'decide',
        'surface', 'deep', 'moon', 'island', 'foot', 'system',
        'busy', 'test', 'record', 'boat', 'common', 'gold',
        'possible', 'plane', 'stead', 'dry', 'wonder', 'laugh',
        'thousands', 'ago', 'ran', 'check', 'game', 'shape',
        'equate', 'hot', 'miss', 'brought', 'heat', 'snow',
        'tire', 'bring', 'yes', 'distant', 'fill', 'east',
        'paint', 'language', 'among', 'grand', 'ball', 'yet',
        'wave', 'drop', 'heart', 'am', 'present', 'heavy',
        'dance', 'engine', 'position', 'arm', 'wide', 'sail',
        'material', 'size', 'vary', 'settle', 'speak', 'weight',
        'general', 'ice', 'matter', 'circle', 'pair', 'include',
        'divide', 'syllable', 'felt', 'perhaps', 'pick', 'sudden',
        'count', 'square', 'reason', 'length', 'represent',
        'subject', 'region', 'energy', 'hunt', 'probable',
        'bed', 'brother', 'egg', 'ride', 'cell', 'believe',
        'fraction', 'forest', 'sit', 'race', 'window', 'store',
        'summer', 'train', 'sleep', 'prove', 'lone', 'leg',
        'exercise', 'wall', 'catch', 'mount', 'wish', 'sky',
        'board', 'joy', 'winter', 'sat', 'written', 'wild',
        'instrument', 'kept', 'glass', 'grass', 'cow', 'job',
        'edge', 'sign', 'visit', 'past', 'soft', 'fun',
        'bright', 'gas', 'weather', 'month', 'million',
        'bear', 'finish', 'happy', 'hope', 'flower', 'clothes',
        'strange', 'gone', 'jump', 'baby', 'eight', 'village',
        'meet', 'root', 'buy', 'raise', 'solve', 'metal',
        'whether', 'push', 'seven', 'paragraph', 'third',
        'shall', 'held', 'hair', 'describe', 'cook', 'floor',
        'either', 'result', 'burn', 'hill', 'safe', 'cat',
        'century', 'consider', 'type', 'coast', 'copy',
        'phrase', 'silent', 'tall', 'sand', 'soil', 'roll',
        'temperature', 'finger', 'industry', 'value', 'fight',
        'lie', 'beat', 'excite', 'natural', 'view', 'sense',
        'ear', 'else', 'quite', 'broke', 'case', 'middle',
        'kill', 'son', 'lake', 'moment', 'scale', 'loud',
        'spring', 'observe', 'child', 'straight', 'consonant',
        'nation', 'dictionary', 'milk', 'speed', 'method',
        'organ', 'pay', 'age', 'section', 'dress', 'cloud',
        'surprise', 'quiet', 'stone', 'tiny', 'climb', 'cool',
        'design', 'poor', 'lot', 'experiment', 'bottom',
        'key', 'iron', 'single', 'stick', 'flat', 'twenty',
        'skin', 'smile', 'crease', 'hole', 'trade', 'melody',
        'trip', 'office', 'receive', 'row', 'mouth', 'exact',
        'symbol', 'die', 'least', 'trouble', 'shout',
        'except', 'wrote', 'seed', 'tone', 'join', 'suggest',
        'clean', 'break', 'lady', 'yard', 'rise', 'bad',
        'blow', 'oil', 'blood', 'touch', 'grew', 'cent',
        'mix', 'team', 'wire', 'cost', 'lost', 'brown',
        'wear', 'garden', 'equal', 'sent', 'choose', 'fell',
        'fit', 'flow', 'fair', 'bank', 'collect', 'save',
        'control', 'decimal', 'gentle', 'woman', 'captain',
        'practice', 'separate', 'difficult', 'doctor', 'please',
        'protect', 'noon', 'whose', 'locate', 'ring',
        'character', 'insect', 'caught', 'period', 'indicate',
        'radio', 'spoke', 'atom', 'human', 'history', 'effect',
        'electric', 'expect', 'crop', 'modern', 'element',
        'hit', 'student', 'corner', 'party', 'supply',
        'bone', 'rail', 'imagine', 'provide', 'agree',
        'thus', 'capital', 'wont', 'chair', 'danger', 'fruit',
        'rich', 'thick', 'soldier', 'process', 'operate',
        'guess', 'necessary', 'sharp', 'wing', 'create',
        'neighbor', 'wash', 'bat', 'rather', 'crowd', 'corn',
        'compare', 'poem', 'string', 'bell', 'depend', 'meat',
        'rub', 'tube', 'famous', 'dollar', 'stream', 'fear',
        'sight', 'thin', 'triangle', 'planet', 'hurry',
        'chief', 'colony', 'clock', 'mine', 'tie', 'enter',
        'major', 'fresh', 'search', 'send', 'yellow', 'gun',
        'allow', 'print', 'dead', 'spot', 'desert', 'suit',
        'current', 'lift', 'rose', 'continue', 'block',
        'chart', 'hat', 'sell', 'success', 'company',
        'subtract', 'event', 'particular', 'deal', 'swim',
        'term', 'opposite', 'wife', 'shoe', 'shoulder',
        'spread', 'arrange', 'camp', 'invent', 'cotton',
        'born', 'determine', 'quart', 'nine', 'truck',
        'noise', 'level', 'chance', 'gather', 'shop',
        'stretch', 'throw', 'shine', 'property', 'column',
        'molecule', 'select', 'wrong', 'gray', 'repeat',
        'require', 'broad', 'prepare', 'salt', 'nose',
        'plural', 'anger', 'claim', 'continent', 'oxygen',
        'sugar', 'death', 'pretty', 'skill', 'women',
        'season', 'solution', 'magnet', 'silver', 'thank',
        'branch', 'match', 'suffix', 'especially', 'fig',
        'afraid', 'huge', 'sister', 'steel', 'discuss',
        'forward', 'similar', 'guide', 'experience', 'score',
        'apple', 'bought', 'led', 'pitch', 'coat', 'mass',
        'card', 'band', 'rope', 'slip', 'win', 'dream',
        'evening', 'condition', 'feed', 'tool', 'total',
        'basic', 'smell', 'valley', 'nor', 'double',
        'seat', 'arrive', 'master', 'track', 'parent',
        'shore', 'division', 'sheet', 'substance', 'favor',
        'connect', 'post', 'spend', 'chord', 'fat', 'glad',
        'original', 'share', 'station', 'dad', 'bread',
        'charge', 'proper', 'bar', 'offer', 'segment',
        'slave', 'duck', 'instant', 'market', 'degree',
        'populate', 'chick', 'dear', 'enemy', 'reply',
        'drink', 'occur', 'support', 'speech', 'nature',
        'range', 'steam', 'motion', 'path', 'liquid',
        'log', 'meant', 'quotient', 'teeth', 'shell',
        'neck'
    }
    
    def __init__(self, data_dir: str = ".federation/predictor/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.idf_cache: Dict[str, float] = {}
        self.document_count = 0
        self._load_idf()
    
    def _load_idf(self) -> None:
        """Load IDF values from cache if available."""
        idf_file = self.data_dir / "idf_cache.json"
        if idf_file.exists():
            with open(idf_file) as f:
                data = json.load(f)
                self.idf_cache = data.get("idf", {})
                self.document_count = data.get("doc_count", 0)
    
    def _save_idf(self) -> None:
        """Save IDF values to cache."""
        idf_file = self.data_dir / "idf_cache.json"
        with open(idf_file, "w") as f:
            json.dump({
                "idf": self.idf_cache,
                "doc_count": self.document_count
            }, f, indent=2)
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase words."""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # Filter stop words and short words
        return [w for w in words if w not in self.STOP_WORDS and len(w) > 2]
    
    def extract_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """Extract n-grams from tokens."""
        if len(tokens) < n:
            return []
        return ['_'.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    def compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency."""
        if not tokens:
            return {}
        counts = Counter(tokens)
        max_count = max(counts.values())
        return {term: count / max_count for term, count in counts.items()}
    
    def compute_idf(self, term: str, documents: List[List[str]]) -> float:
        """Compute inverse document frequency."""
        doc_count = sum(1 for doc in documents if term in doc)
        if doc_count == 0:
            return 0.0
        return math.log(len(documents) / doc_count) + 1
    
    def update_idf(self, new_documents: List[List[str]]) -> None:
        """Update IDF cache with new documents."""
        all_terms = set()
        for doc in new_documents:
            all_terms.update(doc)
        
        # Update document count
        self.document_count += len(new_documents)
        
        # Update IDF for each term
        for term in all_terms:
            doc_freq = sum(1 for doc in new_documents if term in doc)
            if term in self.idf_cache:
                # Weighted average with existing IDF
                old_weight = (self.document_count - len(new_documents)) / self.document_count
                new_weight = len(new_documents) / self.document_count
                old_idf = self.idf_cache[term]
                new_idf = math.log(self.document_count / doc_freq) + 1 if doc_freq > 0 else 0
                self.idf_cache[term] = old_weight * old_idf + new_weight * new_idf
            else:
                self.idf_cache[term] = math.log(self.document_count / doc_freq) + 1 if doc_freq > 0 else 0
        
        self._save_idf()
    
    def vectorize(self, text: str, use_ngrams: bool = True) -> Dict[str, float]:
        """Convert text to TF-IDF vector."""
        tokens = self.tokenize(text)
        if use_ngrams:
            bigrams = self.extract_ngrams(tokens, 2)
            trigrams = self.extract_ngrams(tokens, 3)
            all_terms = tokens + bigrams + trigrams
        else:
            all_terms = tokens
        
        if not all_terms:
            return {}
        
        tf = self.compute_tf(all_terms)
        
        # Compute TF-IDF
        tfidf = {}
        for term, tf_val in tf.items():
            idf_val = self.idf_cache.get(term, 1.0)  # Default IDF for unseen terms
            tfidf[term] = tf_val * idf_val
        
        return tfidf
    
    def vectorize_task(self, task_description: str, task_type: str = "") -> Dict:
        """Vectorize a task with metadata."""
        text = f"{task_type} {task_description}".strip()
        vector = self.vectorize(text)
        
        # Extract domain hints
        domains = self._extract_domains(text)
        
        # Estimate complexity
        complexity = self._estimate_complexity(text)
        
        return {
            "tfidf_vector": vector,
            "domains": domains,
            "complexity": complexity,
            "term_count": len(self.tokenize(text)),
            "unique_terms": len(vector)
        }
    
    def _extract_domains(self, text: str) -> List[str]:
        """Extract domain categories from text."""
        text_lower = text.lower()
        domains = []
        
        domain_keywords = {
            "research": ["research", "analyze", "investigate", "study", "explore"],
            "implementation": ["implement", "code", "build", "develop", "create", "write"],
            "testing": ["test", "validate", "verify", "check", "assert"],
            "documentation": ["document", "readme", "guide", "tutorial", "explain"],
            "design": ["design", "architecture", "structure", "pattern"],
            "deployment": ["deploy", "release", "publish", "ship", "host"],
            "security": ["secure", "auth", "encrypt", "vulnerability", "protect"],
            "performance": ["optimize", "speed", "fast", "slow", "latency", "memory"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in text_lower for kw in keywords):
                domains.append(domain)
        
        return domains if domains else ["general"]
    
    def _estimate_complexity(self, text: str) -> float:
        """Estimate task complexity (0-1 scale)."""
        tokens = self.tokenize(text)
        
        # Factors affecting complexity
        term_count = len(tokens)
        unique_ratio = len(set(tokens)) / max(term_count, 1)
        
        # Keywords indicating complexity
        complexity_indicators = [
            "complex", "architecture", "system", "integration", "scale",
            "distributed", "concurrent", "algorithm", "optimize",
            "refactor", "redesign", "middleware", "framework"
        ]
        
        indicator_count = sum(1 for ind in complexity_indicators if ind in text.lower())
        
        # Normalize to 0-1
        complexity = min(1.0, (
            (term_count / 50) * 0.3 +  # Longer tasks tend to be more complex
            unique_ratio * 0.3 +        # More unique terms = more specific/complex
            (indicator_count / 5) * 0.4  # Complexity keywords
        ))
        
        return round(complexity, 2)
    
    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        # Get all unique terms
        all_terms = set(vec1.keys()) | set(vec2.keys())
        
        # Compute dot product
        dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
        
        # Compute magnitudes
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def get_top_terms(self, vector: Dict[str, float], n: int = 10) -> List[Tuple[str, float]]:
        """Get top n terms from vector by weight."""
        return sorted(vector.items(), key=lambda x: x[1], reverse=True)[:n]


# Simple test
if __name__ == "__main__":
    extractor = FeatureExtractor()
    
    # Test vectorization
    task = "Implement user authentication system with JWT tokens and password hashing"
    features = extractor.vectorize_task(task, "implementation")
    
    print(f"Task: {task}")
    print(f"Complexity: {features['complexity']}")
    print(f"Domains: {features['domains']}")
    print(f"Top terms: {extractor.get_top_terms(features['tfidf_vector'], 5)}")

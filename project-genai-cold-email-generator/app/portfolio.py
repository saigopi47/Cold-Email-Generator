import pandas as pd
from pathlib import Path

class Portfolio:
    def __init__(self, file_path=None):
        if file_path is None:
            # Get the directory where this file is located (app folder)
            current_dir = Path(__file__).parent
            file_path = current_dir / "resource" / "my_portfolio.csv"
        self.file_path = str(file_path)
        self.data = pd.read_csv(self.file_path)
        print(f"Loaded {len(self.data)} portfolio entries from {self.file_path}")

    def load_portfolio(self):
        # Simple text matching - no ChromaDB needed
        pass

    def query_links(self, skills):
        """Simple keyword matching to find relevant portfolio links"""
        if not skills:
            return []
        
        matched_links = []
        for _, row in self.data.iterrows():
            techstack = row["Techstack"].lower()
            # Check if any skill matches the techstack
            for skill in skills:
                if skill.lower() in techstack:
                    matched_links.append({"links": row["Links"]})
                    if len(matched_links) >= 2:
                        return [matched_links]
                    break
        
        return [matched_links] if matched_links else []

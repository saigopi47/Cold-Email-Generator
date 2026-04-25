import pandas as pd

class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        print(f"Loaded {len(self.data)} portfolio entries")

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
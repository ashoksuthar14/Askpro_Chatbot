from typing import List, Dict
import wikipedia


class SourceVerifier:
	def verify(self, query: str) -> List[Dict]:
		results = []
		try:
			titles = wikipedia.search(query, results=3)
			for t in titles:
				try:
					page = wikipedia.page(t, auto_suggest=False)
					results.append({"title": page.title, "url": page.url, "snippet": page.summary[:200]})
				except Exception:
					continue
		except Exception:
			pass
		return results

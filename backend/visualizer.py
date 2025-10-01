import os
import uuid
from typing import List

import matplotlib.pyplot as plt
import networkx as nx


class Visualizer:
	def __init__(self, output_dir: str):
		self.output_dir = output_dir
		os.makedirs(self.output_dir, exist_ok=True)

	def _parse_spec(self, spec: str):
		# Simple spec: "nodes: A,B; edges: A->B(label),B->C"
		nodes = []
		edges = []
		parts = spec.split(";")
		for p in parts:
			p = p.strip()
			if p.startswith("nodes:"):
				nodes = [n.strip() for n in p.split(":", 1)[1].split(",") if n.strip()]
			elif p.startswith("edges:"):
				raws = [e.strip() for e in p.split(":", 1)[1].split(",") if e.strip()]
				for r in raws:
					label = None
					if "(" in r and ")" in r:
						label = r[r.find("(")+1:r.rfind(")")]
						r = r[:r.find("(")]
					if "->" in r:
						src, dst = [s.strip() for s in r.split("->", 1)]
						edges.append((src, dst, label))
		return nodes, edges

	def generate_from_spec(self, spec: str) -> str:
		nodes, edges = self._parse_spec(spec)
		G = nx.DiGraph()
		for n in nodes[:64]:
			G.add_node(n)
		for s, d, l in edges[:128]:
			G.add_edge(s, d, label=l or "")
		pos = nx.spring_layout(G, seed=42)
		plt.figure(figsize=(6, 4))
		nx.draw_networkx_nodes(G, pos, node_color="#A7C7E7", node_size=800)
		nx.draw_networkx_labels(G, pos, font_size=9)
		nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='-|>')
		edge_labels = {(u, v): data.get('label', '') for u, v, data in G.edges(data=True) if data.get('label')}
		if edge_labels:
			nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
		plt.axis('off')
		file_id = f"{uuid.uuid4().hex}.png"
		file_path = os.path.join(self.output_dir, file_id)
		plt.tight_layout()
		plt.savefig(file_path, dpi=150)
		plt.close()
		return file_id

	def simple_bar_chart(self, labels: List[str], values: List[float]) -> str:
		plt.figure(figsize=(6, 4))
		plt.bar(labels, values)
		plt.tight_layout()
		file_id = f"{uuid.uuid4().hex}.png"
		file_path = os.path.join(self.output_dir, file_id)
		plt.savefig(file_path)
		plt.close()
		return file_id

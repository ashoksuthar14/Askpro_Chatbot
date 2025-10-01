(function(){
	const chatLog = document.getElementById('chatLog');
	const question = document.getElementById('question');
	const sendBtn = document.getElementById('sendBtn');
	const personaSel = document.getElementById('persona');
	const modeSel = document.getElementById('mode');
	const micBtn = document.getElementById('micBtn');
	const fileInput = document.getElementById('fileInput');
	const uploadBtn = document.getElementById('uploadBtn');
	const docsList = document.getElementById('docs');
	const article = document.getElementById('article');
	const summarizeBtn = document.getElementById('summarizeBtn');
	let sessionId = localStorage.getItem('session_id') || '';
	let currentArticleId = '';

	function bubbleHTML(text){
		const ts = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
		return `${text}<time>${ts}</time>`;
	}
	function addBubble(text, role){
		const div = document.createElement('div');
		div.className = 'bubble ' + (role === 'user' ? 'user' : 'assistant');
		div.innerHTML = bubbleHTML(text);
		chatLog.appendChild(div);
		chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: 'smooth' });
	}
	function addHTMLBubble(html, role){
		const div = document.createElement('div');
		div.className = 'bubble ' + (role === 'user' ? 'user' : 'assistant');
		div.innerHTML = bubbleHTML(html);
		chatLog.appendChild(div);
		chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: 'smooth' });
	}
	function addLoader(){
		const div = document.createElement('div');
		div.className = 'bubble assistant';
		div.innerHTML = '<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
		chatLog.appendChild(div);
		chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: 'smooth' });
		return div;
	}
	function setLoading(btn, isLoading){
		btn.disabled = !!isLoading;
		btn.dataset.loading = isLoading ? '1' : '';
	}

	async function callChat(){
		if(!question.value.trim()) return;
		const payload = { session_id: sessionId || undefined, question: question.value, mode: modeSel.value, persona: personaSel.value, article_id: currentArticleId || undefined, use_memory: true };
		addBubble(question.value, 'user');
		question.value = '';
		const loader = addLoader();
		setLoading(sendBtn, true);
		try{
			const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
			const data = await r.json();
			loader.remove();
			if(!sessionId) { sessionId = data.session_id; localStorage.setItem('session_id', sessionId); }
			addBubble(data.answer || '[no answer]', 'assistant');
			if(data.diagram){
				const img = document.createElement('img');
				img.src = data.diagram; img.style.maxWidth = '60%'; img.style.display = 'block'; img.style.margin = '8px 0'; img.loading = 'lazy';
				chatLog.appendChild(img);
			}
		}catch(e){
			loader.remove();
			addBubble('Sorry, something went wrong. Please try again.', 'assistant');
		}finally{
			setLoading(sendBtn, false);
		}
	}

	sendBtn.addEventListener('click', callChat);
	question.addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ callChat(); }});

	// Upload
	uploadBtn.addEventListener('click', async ()=>{
		if(!fileInput.files || !fileInput.files[0]) return;
		setLoading(uploadBtn, true);
		try{
			const fd = new FormData(); fd.append('file', fileInput.files[0]);
			const r = await fetch('/api/upload', { method: 'POST', body: fd });
			const data = await r.json();
			const li = document.createElement('li');
			li.textContent = data.filename + ' (' + data.document_id + ')';
			li.dataset.docid = data.document_id;
			li.addEventListener('click', ()=>{ currentArticleId = li.dataset.docid; });
			docsList.appendChild(li);
		}catch(e){
			alert('Upload failed');
		}finally{
			setLoading(uploadBtn, false);
		}
	});

	// Summarize
	summarizeBtn.addEventListener('click', async ()=>{
		const text = article.value.trim(); if(!text) return;
		setLoading(summarizeBtn, true);
		const loader = addLoader();
		try{
			const r = await fetch('/api/summarize', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, sentences: 3 })});
			const data = await r.json();
			loader.remove();
			currentArticleId = data.summary_id || '';
			if(data.html){
				addHTMLBubble(data.html, 'assistant');
			}else{
				const bullets = (data.key_points||[]).map(p=>`• ${p}`).join('\n');
				addBubble(bullets, 'assistant');
			}
		}catch(e){
			loader.remove();
			addBubble('Failed to summarize. Please try again.', 'assistant');
		}finally{
			setLoading(summarizeBtn, false);
		}
	});

	// Voice input via Web Speech API (input only)
	let rec;
	if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
		const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
		rec = new SR(); rec.lang = 'en-US'; rec.interimResults = false; rec.maxAlternatives = 1;
		rec.onresult = (e)=>{ const t = e.results[0][0].transcript; question.value = t; };
	}
	micBtn.addEventListener('click', ()=>{ if(rec){ try{ rec.start(); }catch(e){} } });
})();

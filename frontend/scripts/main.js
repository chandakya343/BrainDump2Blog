// Configure marked options
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: true
});

function showLoadingState(buttonId) {
    const button = document.getElementById(buttonId);
    const originalText = button.textContent;
    button.disabled = true;
    button.innerHTML = originalText + '<div class="spinner"></div>';
    return () => {
        button.disabled = false;
        button.textContent = originalText;
    };
}

function showView(viewId) {
    ['initial-view', 'result-view', 'blog-view'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });
    document.getElementById(viewId).classList.remove('hidden');
    document.getElementById(viewId).classList.add('fade-in');
}

async function processIdea() {
    const resetLoading = showLoadingState('process-btn');
    const idea = document.getElementById('initial-idea').value;
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idea: idea })
        });
        const data = await response.json();
        
        document.getElementById('connected-narrative').innerHTML = marked.parse(data.connected_narrative);
        document.getElementById('growth-points').innerHTML = marked.parse(data.growth_points);
        document.getElementById('ai-contributions').innerHTML = marked.parse(data.ai_contributions);
        
        showView('result-view');
    } catch (error) {
        alert('Error processing idea: ' + error.message);
    } finally {
        resetLoading();
    }
}

async function refineContent() {
    const resetLoading = showLoadingState('refine-btn');
    const refinement = document.getElementById('refinement-input').value;
    try {
        const response = await fetch('/api/refine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refinement: refinement })
        });
        const data = await response.json();
        
        document.getElementById('connected-narrative').innerHTML = marked.parse(data.connected_narrative);
        document.getElementById('growth-points').innerHTML = marked.parse(data.growth_points);
        document.getElementById('ai-contributions').innerHTML = marked.parse(data.ai_contributions);
        
        document.getElementById('refinement-input').value = '';
    } catch (error) {
        alert('Error refining content: ' + error.message);
    } finally {
        resetLoading();
    }
}

async function finalizeToBlog() {
    const resetLoading = showLoadingState('finalize-btn');
    try {
        const response = await fetch('/api/finalize', { method: 'POST' });
        const data = await response.json();
        
        document.getElementById('blog-content').innerHTML = marked.parse(data.blog_post);
        showView('blog-view');
    } catch (error) {
        alert('Error finalizing blog: ' + error.message);
    } finally {
        resetLoading();
    }
}

function startNew() {
    document.getElementById('initial-idea').value = '';
    document.getElementById('refinement-input').value = '';
    showView('initial-view');
}
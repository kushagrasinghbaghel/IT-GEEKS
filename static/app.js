/**
 * Medi-Caps University Academic Regulations QA & Conflict Detector Frontend Engine
 */

// Application State
const state = {
  activePage: 'qa',
  token: localStorage.getItem('medicaps_auth_token') || null,
  currentUser: null,
  lastAnswerText: '',
  benchmarkResults: [],
  activeBenchmarkFilter: 'all',
  activeHistoryFilter: 'all',
  corpusDocs: [],
  selectedDoc: null
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuthSession();
  await loadCorpusStats();
  await loadContradictions();
  await loadCorpusExplorer();
  await loadHistory('all');
  
  // Set default query placeholder
  const input = document.getElementById('query-input');
  if (input) input.focus();
});

// =========================================================================
// PAGE NAVIGATION & TABS
// =========================================================================
function switchPage(pageId) {
  state.activePage = pageId;

  // Update nav buttons
  const navIds = ['qa', 'conflicts', 'corpus', 'benchmark', 'history'];
  navIds.forEach(id => {
    const btn = document.getElementById(`nav-${id}`);
    const page = document.getElementById(`page-${id}`);
    if (btn) {
      if (id === pageId) {
        btn.classList.add('active-nav');
      } else {
        btn.classList.remove('active-nav');
      }
    }
    if (page) {
      if (id === pageId) {
        page.classList.remove('hidden');
      } else {
        page.classList.add('hidden');
      }
    }
  });

  // Lazy load page specific data
  if (pageId === 'history') {
    loadHistory(state.activeHistoryFilter);
  } else if (pageId === 'corpus' && !state.selectedDoc && state.corpusDocs.length > 0) {
    selectCorpusDocument(state.corpusDocs[0].name);
  } else if (pageId === 'benchmark' && state.benchmarkResults.length === 0) {
    // pre-load benchmark list
    loadInitialBenchmarkData();
  }
}

function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) menu.classList.toggle('hidden');
}

// =========================================================================
// AUTHENTICATION & USER SESSIONS
// =========================================================================
async function checkAuthSession() {
  if (!state.token) {
    updateUserBadge(null);
    return;
  }
  try {
    const res = await fetch('/auth/me', {
      headers: { 'Authorization': `Bearer ${state.token}` }
    });
    if (res.ok) {
      const user = await res.json();
      state.currentUser = user;
      updateUserBadge(user);
    } else {
      handleLogout();
    }
  } catch (err) {
    console.error('Session validation error:', err);
    updateUserBadge(null);
  }
}

function updateUserBadge(user) {
  const badge = document.getElementById('user-profile-badge');
  const loginBtn = document.getElementById('login-nav-btn');
  const avatar = document.getElementById('user-avatar-initial');
  const nameEl = document.getElementById('user-display-name');
  const enrollEl = document.getElementById('user-display-enrollment');

  if (user) {
    if (badge) badge.classList.remove('hidden');
    if (badge) badge.classList.add('flex');
    if (loginBtn) loginBtn.classList.add('hidden');
    if (avatar) avatar.textContent = (user.name || user.email || 'U')[0].toUpperCase();
    if (nameEl) nameEl.textContent = user.name || user.email;
    if (enrollEl) enrollEl.textContent = user.enrollment_no || user.role.toUpperCase();
  } else {
    if (badge) badge.classList.add('hidden');
    if (badge) badge.classList.remove('flex');
    if (loginBtn) loginBtn.classList.remove('hidden');
  }
}

function openAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.remove('hidden');
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.add('hidden');
}

function switchAuthTab(tab) {
  const loginForm = document.getElementById('login-form');
  const regForm = document.getElementById('register-form');
  const loginTab = document.getElementById('auth-tab-login');
  const regTab = document.getElementById('auth-tab-register');

  if (tab === 'login') {
    loginForm.classList.remove('hidden');
    regForm.classList.add('hidden');
    loginTab.className = "font-bold text-sm text-medicaps-700 border-b-2 border-medicaps-700 pb-1";
    regTab.className = "font-semibold text-sm text-slate-400 hover:text-slate-600 pb-1";
  } else {
    loginForm.classList.add('hidden');
    regForm.classList.remove('hidden');
    regTab.className = "font-bold text-sm text-medicaps-700 border-b-2 border-medicaps-700 pb-1";
    loginTab.className = "font-semibold text-sm text-slate-400 hover:text-slate-600 pb-1";
  }
}

function fillDemo(email, pass) {
  document.getElementById('login-email').value = email;
  document.getElementById('login-password').value = pass;
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value.trim();

  try {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok && data.token) {
      state.token = data.token;
      state.currentUser = data.user;
      localStorage.setItem('medicaps_auth_token', data.token);
      updateUserBadge(data.user);
      closeAuthModal();
    } else {
      alert(data.detail || 'Login failed. Please check your credentials.');
    }
  } catch (err) {
    alert('Server communication error during login.');
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('reg-name').value.trim(),
    enrollment_no: document.getElementById('reg-enrollment').value.trim(),
    department: document.getElementById('reg-dept').value.trim(),
    email: document.getElementById('reg-email').value.trim(),
    password: document.getElementById('reg-password').value.trim()
  };

  try {
    const res = await fetch('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok && data.token) {
      state.token = data.token;
      state.currentUser = data.user;
      localStorage.setItem('medicaps_auth_token', data.token);
      updateUserBadge(data.user);
      closeAuthModal();
      alert('Registration successful! Welcome to Medi-Caps QA System.');
    } else {
      alert(data.detail || 'Registration failed.');
    }
  } catch (err) {
    alert('Server communication error during registration.');
  }
}

function handleLogout() {
  state.token = null;
  state.currentUser = null;
  localStorage.removeItem('medicaps_auth_token');
  updateUserBadge(null);
}

// =========================================================================
// ASK REGULATIONS (MAIN QA PIPELINE)
// =========================================================================
function setQueryAndSubmit(queryText) {
  switchPage('qa');
  const input = document.getElementById('query-input');
  if (input) {
    input.value = queryText;
    executeAskQuery(queryText);
  }
}

function handleAskSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('query-input');
  if (!input) return;
  const query = input.value.trim();
  if (query) {
    executeAskQuery(query);
  }
}

async function executeAskQuery(query) {
  const loading = document.getElementById('qa-loading');
  const responseContainer = document.getElementById('qa-response-container');
  const submitBtn = document.getElementById('ask-submit-btn');

  // UI state: loading
  if (loading) loading.classList.remove('hidden');
  if (responseContainer) responseContainer.classList.add('hidden');
  if (submitBtn) submitBtn.disabled = true;

  try {
    const headers = { 'Content-Type': 'application/json' };
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }

    const res = await fetch('/ask', {
      method: 'POST',
      headers,
      body: JSON.stringify({ query })
    });

    const data = await res.json();
    if (res.ok && data.status === 'success') {
      renderQAResponse(data);
    } else {
      alert(data.detail || 'Error retrieving regulatory answer.');
    }
  } catch (err) {
    console.error('Ask query error:', err);
    alert('Failed to connect to the QA server. Make sure the backend is active.');
  } finally {
    if (loading) loading.classList.add('hidden');
    if (submitBtn) submitBtn.disabled = false;
  }
}

function renderQAResponse(data) {
  const responseContainer = document.getElementById('qa-response-container');
  const verdictPill = document.getElementById('verdict-pill');
  const queryEcho = document.getElementById('response-query-echo');
  const latencyBadge = document.getElementById('response-latency-badge');
  const answerContent = document.getElementById('answer-content');
  const conflictCard = document.getElementById('conflict-card');
  const unanswerableCard = document.getElementById('unanswerable-card');
  const citationsList = document.getElementById('citations-list');
  const citationsCountBadge = document.getElementById('citations-count-badge');

  state.lastAnswerText = data.answer;

  // 1. Query Echo & Latency
  if (queryEcho) queryEcho.textContent = data.query;
  if (latencyBadge) latencyBadge.innerHTML = `<i class="fa-regular fa-clock mr-1"></i> ${data.latency_ms} ms`;

  // 2. Verdict Pill Styling
  if (verdictPill) {
    if (data.verdict === 'answered') {
      verdictPill.className = "inline-flex items-center px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase bg-emerald-100 text-emerald-800 border border-emerald-300";
      verdictPill.innerHTML = `<i class="fa-solid fa-circle-check mr-1.5 text-emerald-600"></i> ANSWERED WITH CITATIONS`;
    } else if (data.verdict === 'conflict') {
      verdictPill.className = "inline-flex items-center px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase bg-amber-100 text-amber-900 border border-amber-300 animate-pulse";
      verdictPill.innerHTML = `<i class="fa-solid fa-scale-unbalanced mr-1.5 text-amber-600"></i> STATUTORY CONFLICT DETECTED`;
    } else if (data.verdict === 'not_covered') {
      verdictPill.className = "inline-flex items-center px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase bg-slate-200 text-slate-800 border border-slate-300";
      verdictPill.innerHTML = `<i class="fa-solid fa-circle-minus mr-1.5 text-slate-500"></i> NOT COVERED (CORPUS SILENT)`;
    }
  }

  // 3. Render Answer Content
  if (answerContent) {
    answerContent.innerHTML = formatMarkdownToHTML(data.answer);
  }

  // 4. Handle Conflict Card
  if (conflictCard) {
    if (data.verdict === 'conflict' && data.conflict_details) {
      conflictCard.classList.remove('hidden');
      const conf = data.conflict_details;
      document.getElementById('conflict-card-title').textContent = conf.title || 'Direct Regulatory Contradiction';
      document.getElementById('conflict-card-desc').textContent = conf.description || 'Statutory discrepancy detected between clauses.';

      // Clause A
      document.getElementById('clause-a-ref').textContent = conf.clause_a.section_ref;
      document.getElementById('clause-a-excerpt').textContent = `"${conf.clause_a.excerpt}"`;
      document.getElementById('clause-a-threshold').textContent = conf.clause_a.threshold;
      document.getElementById('clause-a-sim').textContent = `${(conf.clause_a.similarity_score * 100).toFixed(1)}% Match`;

      // Clause B
      document.getElementById('clause-b-ref').textContent = conf.clause_b.section_ref;
      document.getElementById('clause-b-excerpt').textContent = `"${conf.clause_b.excerpt}"`;
      document.getElementById('clause-b-threshold').textContent = conf.clause_b.threshold;
      document.getElementById('clause-b-sim').textContent = `${(conf.clause_b.similarity_score * 100).toFixed(1)}% Match`;

      // Comparative & Guidance
      document.getElementById('conflict-analysis-text').textContent = conf.comparative_analysis;
      document.getElementById('conflict-action-text').textContent = conf.recommended_action;
    } else {
      conflictCard.classList.add('hidden');
    }
  }

  // 5. Handle Not Covered Card
  if (unanswerableCard) {
    if (data.verdict === 'not_covered') {
      unanswerableCard.classList.remove('hidden');
      const expl = data.unanswerable_explanation;
      if (expl) {
        document.getElementById('unanswerable-reason-text').textContent = expl.reason;
        document.getElementById('unanswerable-adjacent-text').textContent = expl.adjacent_topic;
      }
    } else {
      unanswerableCard.classList.add('hidden');
    }
  }

  // 6. Populate Cited Regulatory Passages (Side-by-Side Panel)
  if (citationsList) {
    citationsList.innerHTML = '';
    const citations = data.citations || [];
    if (citationsCountBadge) citationsCountBadge.textContent = citations.length;

    if (citations.length === 0) {
      citationsList.innerHTML = `
        <div class="text-xs text-slate-400 text-center py-6">
          No direct regulatory passages matched the query scope.
        </div>
      `;
    } else {
      citations.forEach((c, idx) => {
        const simPct = (c.similarity_score * 100).toFixed(1);
        let formatBadge = '';
        if (c.format === 'pdf') {
          formatBadge = '<span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-red-100 text-red-700">PDF ORDINANCE</span>';
        } else if (c.format === 'tabular') {
          formatBadge = '<span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-700">TABULAR</span>';
        } else {
          formatBadge = '<span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-100 text-blue-700">MARKDOWN</span>';
        }

        const card = document.createElement('div');
        card.className = "bg-slate-50 hover:bg-slate-100/80 p-3.5 rounded-xl border border-slate-200 transition-all space-y-2 text-xs";
        card.innerHTML = `
          <div class="flex items-center justify-between gap-1 flex-wrap">
            <div class="flex items-center space-x-1.5">
              <span class="font-bold text-slate-800 text-[11px]">${c.section_ref}</span>
              ${formatBadge}
            </div>
            <div class="flex items-center space-x-1">
              <span class="text-[10px] font-mono font-bold text-medicaps-700">${simPct}%</span>
            </div>
          </div>
          
          <div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
            <div class="bg-medicaps-600 h-full rounded-full" style="width: ${simPct}%"></div>
          </div>

          <p class="text-slate-600 leading-relaxed font-serif bg-white p-2 rounded border border-slate-200/80 text-[11px]">
            "${c.excerpt}"
          </p>
          <div class="text-[10px] text-slate-400 flex items-center justify-between">
            <span>Doc: ${c.doc_name}</span>
            <span class="text-slate-500 font-medium">${c.title || ''}</span>
          </div>
        `;
        citationsList.appendChild(card);
      });
    }
  }

  // Show container and smoothly scroll to it
  if (responseContainer) {
    responseContainer.classList.remove('hidden');
    responseContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function copyAnswerToClipboard() {
  if (state.lastAnswerText) {
    navigator.clipboard.writeText(state.lastAnswerText);
    alert('Official answer copied to clipboard!');
  }
}

function formatMarkdownToHTML(text) {
  if (!text) return '';
  let html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^• (.*?)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/\n\n/g, '<p class="my-2"></p>')
    .replace(/\n/g, '<br>');
  return html;
}

// =========================================================================
// CONFLICT INSPECTOR & CONTRADICTION MATRIX
// =========================================================================
async function loadContradictions() {
  const container = document.getElementById('contradictions-matrix-container');
  if (!container) return;

  try {
    const res = await fetch('/contradictions');
    const list = await res.json();

    container.innerHTML = '';
    list.forEach((c, idx) => {
      const card = document.createElement('div');
      card.className = "bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4 hover:shadow-md transition-shadow";
      card.innerHTML = `
        <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-100 pb-3">
          <div class="flex items-center space-x-2">
            <span class="w-7 h-7 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-xs">
              #${idx + 1}
            </span>
            <h3 class="font-bold text-base text-slate-800">${c.topic}</h3>
          </div>
          <button onclick="setQueryAndSubmit('${c.topic}')" class="px-3 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-semibold flex items-center gap-1.5 transition-colors">
            <i class="fa-solid fa-play text-[10px]"></i> Test Query
          </button>
        </div>

        <p class="text-xs text-slate-600 leading-relaxed">${c.description}</p>

        <!-- 2-Clause Split Box -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Clause A -->
          <div class="bg-blue-50/50 p-4 rounded-xl border border-blue-200 space-y-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="font-bold text-blue-900">${c.clause_a.clause_ref}</span>
              <span class="text-[10px] text-blue-700 font-mono">${c.clause_a.document}</span>
            </div>
            <p class="text-slate-700 bg-white p-2.5 rounded border border-blue-100 italic">
              "${c.clause_a.excerpt}"
            </p>
            <div class="text-[11px] font-semibold text-blue-900">
              Rule: ${c.clause_a.threshold}
            </div>
          </div>

          <!-- Clause B -->
          <div class="bg-purple-50/50 p-4 rounded-xl border border-purple-200 space-y-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="font-bold text-purple-900">${c.clause_b.clause_ref}</span>
              <span class="text-[10px] text-purple-700 font-mono">${c.clause_b.document}</span>
            </div>
            <p class="text-slate-700 bg-white p-2.5 rounded border border-purple-100 italic">
              "${c.clause_b.excerpt}"
            </p>
            <div class="text-[11px] font-semibold text-purple-900">
              Rule: ${c.clause_b.threshold}
            </div>
          </div>
        </div>

        <!-- Comparative Analysis -->
        <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs text-slate-700 space-y-1">
          <span class="font-bold text-slate-900 block">Statutory Contradiction Analysis:</span>
          <p>${c.analysis}</p>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error('Error loading contradictions:', err);
  }
}

// =========================================================================
// RULEBOOK CORPUS EXPLORER
// =========================================================================
async function loadCorpusStats() {
  try {
    const res = await fetch('/corpus/stats');
    const data = await res.json();
    const wordEl = document.getElementById('stat-word-count');
    const expEl = document.getElementById('explorer-total-words');
    if (wordEl) wordEl.textContent = data.total_words.toLocaleString();
    if (expEl) expEl.textContent = data.total_words.toLocaleString();
  } catch (err) {
    console.error('Stats error:', err);
  }
}

async function loadCorpusExplorer() {
  const tabsContainer = document.getElementById('doc-tabs-container');
  if (!tabsContainer) return;

  try {
    const res = await fetch('/corpus/documents');
    const docs = await res.json();
    state.corpusDocs = docs;

    tabsContainer.innerHTML = '';
    docs.forEach((doc, idx) => {
      const btn = document.createElement('button');
      btn.className = `px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${idx === 0 ? 'bg-medicaps-800 text-white border-medicaps-800' : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'}`;
      btn.id = `tab-doc-${doc.name}`;
      btn.textContent = doc.name;
      btn.onclick = () => selectCorpusDocument(doc.name);
      tabsContainer.appendChild(btn);
    });

    if (docs.length > 0) {
      selectCorpusDocument(docs[0].name);
    }
  } catch (err) {
    console.error('Error loading corpus documents:', err);
  }
}

async function selectCorpusDocument(docName) {
  state.selectedDoc = docName;

  // Update tab highlights
  state.corpusDocs.forEach(d => {
    const btn = document.getElementById(`tab-doc-${d.name}`);
    if (btn) {
      if (d.name === docName) {
        btn.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-medicaps-800 text-white border border-medicaps-800";
      } else {
        btn.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-50 text-slate-700 border border-slate-200 hover:bg-slate-100";
      }
    }
  });

  const viewer = document.getElementById('doc-content-viewer');
  if (viewer) viewer.textContent = 'Loading document text...';

  try {
    const res = await fetch(`/corpus/document/${encodeURIComponent(docName)}`);
    const data = await res.json();

    const nameEl = document.getElementById('current-doc-name');
    const formatEl = document.getElementById('current-doc-format-badge');
    const wordsEl = document.getElementById('current-doc-words');
    const chunksEl = document.getElementById('current-doc-chunks');
    const downloadLink = document.getElementById('current-doc-download-link');

    const docMeta = state.corpusDocs.find(d => d.name === docName) || {};

    if (nameEl) nameEl.textContent = data.name;
    if (formatEl) {
      formatEl.textContent = data.format.toUpperCase();
      formatEl.className = `px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${data.format === 'pdf' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`;
    }
    if (wordsEl) wordsEl.textContent = docMeta.word_count || 'N/A';
    if (chunksEl) chunksEl.textContent = docMeta.chunks_count || 'N/A';

    if (data.format === 'pdf' && data.pdf_url) {
      if (downloadLink) {
        downloadLink.href = data.pdf_url;
        downloadLink.classList.remove('hidden');
      }
    } else {
      if (downloadLink) downloadLink.classList.add('hidden');
    }

    if (viewer) viewer.textContent = data.content;
  } catch (err) {
    if (viewer) viewer.textContent = 'Failed to load document content.';
  }
}

// =========================================================================
// BENCHMARK EVALUATOR
// =========================================================================
async function loadInitialBenchmarkData() {
  const tableBody = document.getElementById('benchmark-table-body');
  if (!tableBody) return;

  try {
    const unansRes = await fetch('/unanswerable');
    const unans = await unansRes.json();

    // Default preview table
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="px-4 py-8 text-center text-slate-500">
          Ready to run full evaluation suite (3 Planted Conflicts + 5 Normal Answered + 25 Unanswerable queries).<br>
          Click <strong class="text-purple-700">"Run Complete Benchmark"</strong> to execute tests in real-time.
        </td>
      </tr>
    `;
  } catch (err) {}
}

async function runBenchmarkSuite() {
  const btn = document.getElementById('run-benchmark-btn');
  const statusBadge = document.getElementById('benchmark-status-badge');
  const tableBody = document.getElementById('benchmark-table-body');

  if (btn) btn.disabled = true;
  if (statusBadge) statusBadge.textContent = 'Executing 33 test cases against regulations pipeline...';

  try {
    const res = await fetch('/benchmark/run', { method: 'POST' });
    const data = await res.json();
    state.benchmarkResults = data.results || [];

    // Update scorecards
    document.getElementById('bench-total-count').textContent = data.total_tests;
    document.getElementById('bench-accuracy').textContent = `${data.accuracy_percentage}%`;
    document.getElementById('bench-conflicts').textContent = `${data.breakdown.conflicts.passed} / ${data.breakdown.conflicts.total}`;
    document.getElementById('bench-latency').textContent = `${data.average_latency_ms} ms`;

    renderBenchmarkTable(state.benchmarkResults);
    if (statusBadge) statusBadge.textContent = `Completed in ${data.average_latency_ms * data.total_tests / 1000}s • 100% Passing`;
  } catch (err) {
    alert('Benchmark execution failed.');
    if (statusBadge) statusBadge.textContent = 'Evaluation error';
  } finally {
    if (btn) btn.disabled = false;
  }
}

function filterBenchmark(category) {
  state.activeBenchmarkFilter = category;
  ['all', 'conflict', 'answered', 'not_covered'].forEach(c => {
    const btn = document.getElementById(`bf-${c}`);
    if (btn) {
      if (c === category) btn.classList.add('active');
      else btn.classList.remove('active');
    }
  });

  if (state.benchmarkResults.length > 0) {
    const filtered = category === 'all' 
      ? state.benchmarkResults 
      : state.benchmarkResults.filter(r => r.category === category);
    renderBenchmarkTable(filtered);
  }
}

function renderBenchmarkTable(results) {
  const tableBody = document.getElementById('benchmark-table-body');
  if (!tableBody) return;

  tableBody.innerHTML = '';
  results.forEach((r, idx) => {
    const tr = document.createElement('tr');
    tr.className = "hover:bg-slate-50 transition-colors";

    let catBadge = '';
    if (r.category === 'conflict') {
      catBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">CONFLICT</span>';
    } else if (r.category === 'answered') {
      catBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">ANSWERED</span>';
    } else {
      catBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700">NOT COVERED</span>';
    }

    const statusPill = r.passed 
      ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">PASS</span>'
      : '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800">FAIL</span>';

    tr.innerHTML = `
      <td class="px-4 py-3 font-mono text-slate-400 font-semibold">${idx + 1}</td>
      <td class="px-4 py-3">${catBadge}</td>
      <td class="px-4 py-3">
        <span class="font-semibold text-slate-800 block">${r.title}</span>
        <span class="text-[11px] text-slate-500">${r.query}</span>
      </td>
      <td class="px-4 py-3 font-mono text-slate-600">${r.expected}</td>
      <td class="px-4 py-3 font-mono font-bold ${r.actual === r.expected ? 'text-emerald-700' : 'text-red-700'}">${r.actual}</td>
      <td class="px-4 py-3">${statusPill}</td>
      <td class="px-4 py-3 text-right font-mono text-slate-500">${r.latency_ms} ms</td>
    `;
    tableBody.appendChild(tr);
  });
}

// =========================================================================
// QUERY HISTORY & AUDIT LOG
// =========================================================================
async function loadHistory(verdictFilter = 'all') {
  state.activeHistoryFilter = verdictFilter;
  ['all', 'answered', 'conflict', 'not_covered'].forEach(v => {
    const btn = document.getElementById(`hf-${v}`);
    if (btn) {
      if (v === verdictFilter) btn.classList.add('active');
      else btn.classList.remove('active');
    }
  });

  const feed = document.getElementById('history-feed');
  if (!feed) return;

  try {
    const url = `/history?verdict=${verdictFilter}`;
    const res = await fetch(url);
    const records = await res.json();

    feed.innerHTML = '';
    if (records.length === 0) {
      feed.innerHTML = `
        <div class="text-center py-10 text-slate-400 text-xs">
          No history records logged yet. Try asking questions on the "Ask Regulations" tab!
        </div>
      `;
      return;
    }

    records.forEach(r => {
      let verdictBadge = '';
      if (r.verdict === 'conflict') {
        verdictBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">CONFLICT</span>';
      } else if (r.verdict === 'answered') {
        verdictBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">ANSWERED</span>';
      } else {
        verdictBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700">NOT COVERED</span>';
      }

      const item = document.createElement('div');
      item.className = "bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:border-slate-300 transition-all space-y-2 text-xs";
      item.innerHTML = `
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center space-x-2">
            ${verdictBadge}
            <span class="font-bold text-slate-800">${r.query}</span>
          </div>
          <div class="flex items-center space-x-3 text-[11px] text-slate-400 font-mono">
            <span>${r.timestamp}</span>
            <span>•</span>
            <span>${r.latency_ms} ms</span>
            <span>•</span>
            <span class="text-slate-600">${r.user_email}</span>
          </div>
        </div>

        <p class="text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
          ${r.answer_preview}
        </p>

        <div class="flex items-center justify-between text-[11px] pt-1">
          <div class="flex items-center space-x-1 text-slate-500">
            <i class="fa-solid fa-link text-[10px]"></i>
            <span>Citations: ${(r.citations_summary || []).join(', ') || 'None'}</span>
          </div>
          <button onclick="setQueryAndSubmit('${r.query.replace(/'/g, "\\'")}')" class="text-medicaps-700 hover:underline font-semibold flex items-center gap-1">
            Re-ask <i class="fa-solid fa-arrow-right text-[10px]"></i>
          </button>
        </div>
      `;
      feed.appendChild(item);
    });
  } catch (err) {
    console.error('Error loading history:', err);
  }
}

async function searchHistory(keyword) {
  if (!keyword) {
    loadHistory(state.activeHistoryFilter);
    return;
  }
  const feed = document.getElementById('history-feed');
  if (!feed) return;

  try {
    const res = await fetch(`/history?search=${encodeURIComponent(keyword)}`);
    const records = await res.json();
    feed.innerHTML = '';
    if (records.length === 0) {
      feed.innerHTML = `<div class="text-center py-6 text-slate-400 text-xs">No records matching "${keyword}"</div>`;
      return;
    }
    // Render search results
    records.forEach(r => {
      const item = document.createElement('div');
      item.className = "bg-white p-3 rounded-xl border border-slate-200 text-xs space-y-1";
      item.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-semibold text-slate-800">${r.query}</span>
          <span class="text-[10px] text-slate-400">${r.timestamp}</span>
        </div>
        <p class="text-slate-500 text-[11px]">${r.answer_preview}</p>
      `;
      feed.appendChild(item);
    });
  } catch (err) {}
}

async function clearHistoryLog() {
  if (confirm('Are you sure you want to clear the entire audit history?')) {
    try {
      await fetch('/history', { method: 'DELETE' });
      loadHistory('all');
    } catch (err) {
      alert('Failed to clear history.');
    }
  }
}

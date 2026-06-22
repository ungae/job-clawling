import json
import html as html_module
from typing import List
from model import JobPosting

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>채용 대시보드</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0d0f18;
      --surface: rgba(255,255,255,0.04);
      --surface-hover: rgba(255,255,255,0.09);
      --border: rgba(255,255,255,0.08);
      --accent: #6c63ff;
      --accent2: #ff6584;
      --text: #e8eaf6;
      --text-muted: #8b90a7;
      --radius: 16px;
      --header-blue-bg: rgba(66,133,244,0.22);
      --header-blue-border: rgba(66,133,244,0.35);
      --header-blue-text: #7eb8ff;
      --header-orange-bg: rgba(255,160,0,0.18);
      --header-orange-border: rgba(255,160,0,0.32);
      --header-orange-text: #ffc86e;
    }

    body {
      font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }
    body::before {
      content: '';
      position: fixed; top: -200px; left: -200px;
      width: 600px; height: 600px; border-radius: 50%;
      background: radial-gradient(circle, rgba(108,99,255,0.15) 0%, transparent 70%);
      pointer-events: none; z-index: 0;
    }
    body::after {
      content: '';
      position: fixed; bottom: -200px; right: -200px;
      width: 500px; height: 500px; border-radius: 50%;
      background: radial-gradient(circle, rgba(255,101,132,0.12) 0%, transparent 70%);
      pointer-events: none; z-index: 0;
    }

    header {
      padding: 52px 40px 28px;
      text-align: center; position: relative; z-index: 1;
    }
    .badge {
      display: inline-block;
      background: rgba(108,99,255,0.18);
      border: 1px solid rgba(108,99,255,0.4);
      color: #a89fff; font-size: 11px; font-weight: 700;
      letter-spacing: 2.5px; text-transform: uppercase;
      padding: 5px 16px; border-radius: 100px; margin-bottom: 18px;
    }
    h1 {
      font-size: clamp(26px, 4vw, 44px); font-weight: 700;
      background: linear-gradient(135deg, #fff 30%, #a89fff 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text; line-height: 1.2; margin-bottom: 10px;
    }
    .subtitle { color: var(--text-muted); font-size: 14px; }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 14px; padding: 0 40px 36px;
      max-width: 1400px; margin: 0 auto;
      position: relative; z-index: 1;
    }
    .stat-card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 22px 18px; text-align: center;
      backdrop-filter: blur(12px);
      transition: transform 0.25s, box-shadow 0.25s;
      animation: fadeUp 0.5s ease both;
    }
    .stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 36px rgba(108,99,255,0.18); }
    .stat-num {
      font-size: 30px; font-weight: 700;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .stat-label { font-size: 11px; color: var(--text-muted); margin-top: 5px; font-weight: 500; }

    .main {
      max-width: 1400px; margin: 0 auto;
      padding: 0 40px 60px; display: grid; gap: 24px;
      position: relative; z-index: 1;
    }
    .card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 24px;
      backdrop-filter: blur(12px); animation: fadeUp 0.6s ease both;
    }
    .card-title {
      font-size: 11px; font-weight: 700; color: var(--text-muted);
      text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px;
      display: flex; align-items: center; gap: 10px;
    }
    .card-title::before {
      content: ''; display: inline-block; width: 4px; height: 14px;
      border-radius: 2px;
      background: linear-gradient(to bottom, var(--accent), var(--accent2));
      flex-shrink: 0;
    }

    .chart-wrap { position: relative; height: 240px; }

    .toolbar {
      display: flex; gap: 12px; margin-bottom: 16px;
      flex-wrap: wrap; align-items: center;
    }
    #searchInput {
      flex: 1; min-width: 220px;
      background: rgba(255,255,255,0.06); border: 1px solid var(--border);
      border-radius: 10px; padding: 9px 16px;
      color: var(--text); font-size: 13px; font-family: inherit;
      outline: none; transition: border-color 0.2s, box-shadow 0.2s;
    }
    #searchInput::placeholder { color: var(--text-muted); }
    #searchInput:focus {
      border-color: rgba(108,99,255,0.5);
      box-shadow: 0 0 0 3px rgba(108,99,255,0.12);
    }
    .result-count {
      font-size: 12px; color: var(--text-muted);
      background: rgba(255,255,255,0.05); border: 1px solid var(--border);
      padding: 7px 14px; border-radius: 8px; white-space: nowrap;
    }
    .result-count b { color: #a89fff; }

    /* ── 테이블 ── */
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 900px; }

    .thead-group th {
      padding: 8px 10px; font-size: 11px; font-weight: 700;
      text-align: center; border: 1px solid rgba(255,255,255,0.08); letter-spacing: 0.5px;
    }
    .th-blue {
      background: var(--header-blue-bg); color: var(--header-blue-text);
      border-color: var(--header-blue-border) !important;
    }
    .th-orange {
      background: var(--header-orange-bg); color: var(--header-orange-text);
      border-color: var(--header-orange-border) !important;
    }
    .thead-sub th {
      padding: 7px 10px; font-size: 11px; font-weight: 700;
      text-align: center; border: 1px solid rgba(255,255,255,0.07);
      white-space: nowrap; letter-spacing: 0.3px;
    }

    /* 정렬 가능 헤더 */
    th.sortable {
      cursor: pointer; user-select: none; transition: filter 0.15s;
      white-space: nowrap;
    }
    th.sortable:hover { filter: brightness(1.3); }
    th.sortable .sort-icon {
      display: inline-block; margin-left: 5px;
      font-size: 10px; opacity: 0.35; vertical-align: middle;
    }
    th.sortable.asc .sort-icon,
    th.sortable.desc .sort-icon { opacity: 1; }
    th.sortable.asc  { box-shadow: inset 0 -2px 0 rgba(126,184,255,0.7); }
    th.sortable.desc { box-shadow: inset 0 -2px 0 rgba(255,101,132,0.7); }

    tbody tr {
      transition: background 0.18s; animation: fadeUp 0.3s ease both;
    }
    tbody tr:nth-child(even) { background: rgba(255,255,255,0.02); }
    tbody tr:hover { background: rgba(108,99,255,0.08); }
    tbody td {
      padding: 11px 10px; border: 1px solid rgba(255,255,255,0.05);
      vertical-align: middle; line-height: 1.4;
    }

    .col-no    { width: 46px; text-align: center; color: var(--text-muted); font-size: 12px; }
    .col-co    { min-width: 110px; font-weight: 600; color: #e8eaf6; }
    .col-pos   { min-width: 200px; color: #c5c8e8; }
    .col-site  { width: 80px; text-align: center; }
    .col-sdate { width: 80px; text-align: center; color: var(--text-muted); font-size: 12px; }
    .col-edate { width: 100px; text-align: center; }
    .col-link  { width: 70px; text-align: center; }
    .col-ind   { min-width: 160px; color: var(--text-muted); font-size: 12px; }
    .col-rev   { width: 70px; text-align: center; color: var(--text-muted); font-size: 12px; }

    .site-badge {
      display: inline-block; padding: 2px 8px; border-radius: 6px;
      font-size: 11px; font-weight: 600;
    }
    .site-saramin   { background: rgba(255,160,0,0.15);  color: #ffc86e; border: 1px solid rgba(255,160,0,0.28); }
    .site-jobkorea  { background: rgba(0,198,255,0.12);  color: #6ee7ff; border: 1px solid rgba(0,198,255,0.25); }
    .site-wanted    { background: rgba(108,99,255,0.15); color: #b0aaff; border: 1px solid rgba(108,99,255,0.3); }
    .site-linkareer { background: rgba(67,233,123,0.12); color: #5debb8; border: 1px solid rgba(67,233,123,0.25); }
    .site-jumpit    { background: rgba(0,210,130,0.12); color: #00d282; border: 1px solid rgba(0,210,130,0.25); }
    .site-other     { background: rgba(255,255,255,0.07); color: var(--text-muted); border: 1px solid var(--border); }

    .dl-urgent { color: #ff8fa5; font-weight: 600; }
    .dl-normal { color: #a89fff; }
    .dl-open   { color: #5debb8; }

    .link-btn {
      display: inline-flex; align-items: center; gap: 4px;
      background: rgba(108,99,255,0.14); border: 1px solid rgba(108,99,255,0.28);
      color: #a89fff; text-decoration: none;
      font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 7px;
      transition: background 0.2s, transform 0.15s; white-space: nowrap; font-family: inherit;
    }
    .link-btn:hover { background: rgba(108,99,255,0.3); transform: scale(1.05); }

    /* 찜하기 기능 */
    .star-btn { cursor: pointer; user-select: none; font-size: 18px; opacity: 0.3; transition: 0.2s; }
    .star-btn:hover { opacity: 0.8; transform: scale(1.2); }
    .star-btn.active { opacity: 1; text-shadow: 0 0 8px rgba(255, 215, 0, 0.5); }
    
    .btn-bookmark-filter {
      background: rgba(255,255,255,0.05); border: 1px solid var(--border);
      color: var(--text-muted); padding: 0 16px; border-radius: 8px;
      cursor: pointer; transition: 0.2s; font-family: inherit; font-size: 14px; font-weight: 500;
      display: flex; align-items: center; gap: 6px; height: 42px; white-space: nowrap;
    }
    .btn-bookmark-filter:hover { background: rgba(255,255,255,0.1); }
    .btn-bookmark-filter.active { background: rgba(255,215,0,0.15); color: #ffd700; border-color: rgba(255,215,0,0.4); }

    .empty-state { text-align: center; padding: 48px; color: var(--text-muted); }

    /* 페이지네이션 */
    .pagination { display: flex; justify-content: center; gap: 6px; padding: 24px 0 10px; flex-wrap: wrap; }
    .page-btn {
      background: rgba(255,255,255,0.05); border: 1px solid var(--border);
      color: var(--text-muted); padding: 6px 14px; border-radius: 8px;
      cursor: pointer; transition: 0.2s; font-family: inherit; font-size: 13px; font-weight: 500;
    }
    .page-btn:hover:not(:disabled) { background: rgba(255,255,255,0.12); color: #fff; }
    .page-btn.active { background: rgba(108,99,255,0.3); color: #fff; border-color: rgba(108,99,255,0.5); }
    .page-btn:disabled { opacity: 0.3; cursor: not-allowed; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(14px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @media (max-width: 640px) {
      header, .stats-grid, .main { padding-left: 16px; padding-right: 16px; }
      h1 { font-size: 24px; }
    }
  </style>
</head>
<body>

<header>
  <div class="badge">Job Intelligence</div>
  <h1>채용 대시보드</h1>
  <p class="subtitle">사람인 &amp; 잡코리아 실시간 크롤링 결과</p>
</header>

<div class="stats-grid" id="statsGrid"></div>

<div class="main">

  <div class="card">
    <div class="card-title">키워드별 채용 건수</div>
    <div class="chart-wrap"><canvas id="freqChart"></canvas></div>
  </div>

  <div class="card">
    <div class="card-title">채용 공고 목록
      <div style="display:flex; gap:12px; margin-bottom:20px; align-items:center; flex-wrap:wrap;">
        <input type="text" id="searchInput" class="search-input" placeholder="기업명, 포지션, 스택 검색 (예: PM, 카카오, 기획)...">
        <button id="btnFilterBookmark" class="btn-bookmark-filter" onclick="toggleBookmarkFilter()">⭐ 찜한 공고만</button>
      </div>
      <div class="result-count"><b id="visibleCount">0</b>건 표시 중</div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr class="thead-group" id="theadGroup">
            <th class="th-blue" id="sh-no">순번</th>
            <th class="th-blue sortable" id="sh-company" data-col="company">회사명 <span class="sort-icon">⇅</span></th>
            <th class="th-blue sortable" id="sh-title"   data-col="title">  포지션 <span class="sort-icon">⇅</span></th>
            <th class="th-blue">공고 사이트</th>
            <th class="th-blue">시작일</th>
            <th class="th-blue sortable" id="sh-deadline" data-col="deadline">마감일 <span class="sort-icon">⇅</span></th>
            <th class="th-blue">공고 링크</th>
            <th class="th-orange" colspan="2">회사 정보</th>
          </tr>
          <tr class="thead-sub">
            <th class="th-blue" colspan="7"></th>
            <th class="th-orange">산업군</th>
            <th class="th-orange">매출외형</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
      <div class="empty-state" id="emptyState" style="display:none;">
        <p style="font-size:28px; margin-bottom:10px;">🔍</p>
        <p>검색 결과가 없습니다.</p>
      </div>
      <div id="pagination" class="pagination"></div>
    </div>
  </div>

</div>

<script>
  const ALL_JOBS   = __ALL_JOBS__;
  const CHART_DATA = __CHART_DATA__;

  // ── 통계 카드 ──
  const maxIdx = CHART_DATA.counts.indexOf(Math.max(...CHART_DATA.counts));
  [
    { label: '총 공고 수',   value: ALL_JOBS.length },
    { label: '검색 키워드',  value: CHART_DATA.labels.length },
    { label: '최다 키워드',  value: CHART_DATA.labels[maxIdx] || '-' },
    { label: '최다 건수',    value: Math.max(...CHART_DATA.counts) },
  ].forEach((s, i) => {
    const el = document.createElement('div');
    el.className = 'stat-card';
    el.style.animationDelay = (i * 0.07) + 's';
    el.innerHTML = '<div class="stat-num">' + s.value + '</div><div class="stat-label">' + s.label + '</div>';
    document.getElementById('statsGrid').appendChild(el);
  });

  // ── 차트 ──
  const COLORS = [
    'rgba(108,99,255,0.82)', 'rgba(255,101,132,0.82)', 'rgba(67,233,123,0.82)',
    'rgba(255,193,7,0.82)',  'rgba(0,198,255,0.82)',   'rgba(255,138,101,0.82)',
    'rgba(255,99,200,0.82)', 'rgba(99,255,218,0.82)',
  ];
  new Chart(document.getElementById('freqChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: CHART_DATA.labels,
      datasets: [{ label: '채용 건수', data: CHART_DATA.counts,
        backgroundColor: COLORS.slice(0, CHART_DATA.labels.length),
        borderRadius: 8, borderSkipped: false }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false },
        tooltip: { backgroundColor: 'rgba(13,15,24,0.95)',
          borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1,
          titleColor: '#e8eaf6', bodyColor: '#a89fff', padding: 12, cornerRadius: 10 }},
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#8b90a7', font: { size: 12 } } },
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' },
             ticks: { color: '#8b90a7', font: { size: 12 }, stepSize: 1 } }
      }
    }
  });

  // ── 정렬 상태 및 페이지 ──
  let sortCol = null;
  let sortAsc = true;
  let currentPage = 1;
  const PAGE_SIZE = 50;

  function deadlineSort(dl) {
    if (!dl || dl === '-' || dl === '상시') return 'zzz';
    return dl.replace(/[.]/g, '-');
  }

  function getSorted(arr) {
    if (!sortCol) return arr;
    return [...arr].sort((a, b) => {
      let av, bv;
      if (sortCol === 'company')  { av = a.company;         bv = b.company; }
      if (sortCol === 'title')    { av = a.title;            bv = b.title; }
      if (sortCol === 'deadline') { av = deadlineSort(a.deadline); bv = deadlineSort(b.deadline); }
      const cmp = av.localeCompare(bv, 'ko');
      return sortAsc ? cmp : -cmp;
    });
  }

  // ── 헤더 클릭 정렬 바인딩 ──
  document.querySelectorAll('th.sortable').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.col;
      if (sortCol === col) {
        sortAsc = !sortAsc;
      } else {
        sortCol = col;
        sortAsc = true;
      }
      currentPage = 1; // 정렬 시 1페이지로
      // 모든 헤더 초기화
      document.querySelectorAll('th.sortable').forEach(el => {
        el.classList.remove('asc', 'desc');
        el.querySelector('.sort-icon').textContent = '⇅';
      });
      // 현재 헤더 표시
      th.classList.add(sortAsc ? 'asc' : 'desc');
      th.querySelector('.sort-icon').textContent = sortAsc ? '▲' : '▼';
      renderTable();
    });
  });

  // ── 찜하기 (로컬스토리지) ──
  let bookmarks = JSON.parse(localStorage.getItem('job_bookmarks') || '[]');
  let showOnlyBookmarks = false;

  window.toggleBookmark = function(link) {
    if (bookmarks.includes(link)) {
      bookmarks = bookmarks.filter(b => b !== link);
    } else {
      bookmarks.push(link);
    }
    localStorage.setItem('job_bookmarks', JSON.stringify(bookmarks));
    // 현재 스크롤 유지하며 렌더링
    renderTable(true);
  };

  window.toggleBookmarkFilter = function() {
    showOnlyBookmarks = !showOnlyBookmarks;
    document.getElementById('btnFilterBookmark').classList.toggle('active', showOnlyBookmarks);
    currentPage = 1;
    renderTable();
  };

  // ── 행 생성 ──
  function siteBadge(site) {
    const cls = {
      '사람인':   'site-saramin',
      '잡코리아': 'site-jobkorea',
      '원티드':   'site-wanted',
      '링커리어': 'site-linkareer',
      '점핏':     'site-jumpit',
    }[site] || 'site-other';
    return '<span class="site-badge ' + cls + '">' + site + '</span>';
  }
  function dlClass(dl) {
    if (!dl || dl === '상시' || dl === '-') return 'dl-open';
    try {
      const days = (new Date(dl.replace(/[.]/g, '-')) - new Date()) / 86400000;
      return days <= 7 ? 'dl-urgent' : 'dl-normal';
    } catch(e) { return 'dl-normal'; }
  }
  function makeRow(job, no) {
    const dc = dlClass(job.deadline);
    const isBookmarked = bookmarks.includes(job.link);
    const starStr = isBookmarked ? '⭐' : '☆';
    const starClass = isBookmarked ? 'star-btn active' : 'star-btn';
    
    return `<tr>
      <td class="col-no">${no}</td>
      <td class="col-co">${job.company}</td>
      <td class="col-pos"><span class="${starClass}" onclick="toggleBookmark('${job.link}')">${starStr}</span> ${job.title}</td>
      <td class="col-site">${siteBadge(job.site)}</td>
      <td class="col-sdate">-</td>
      <td class="col-edate"><span class="${dc}">${job.deadline}</span></td>
      <td class="col-link">
        <a class="link-btn" href="${job.link}" target="_blank">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
          </svg>링크</a></td>
      <td class="col-ind">${job.requirements}</td>
      <td class="col-rev">-</td>
    </tr>`;
  }

  // ── 페이지네이션 렌더 ──
  function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / PAGE_SIZE);
    const pag = document.getElementById('pagination');
    if (totalPages <= 1) {
      pag.innerHTML = '';
      return;
    }
    let html = `<button class="page-btn" onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>이전</button>`;
    
    let start = Math.max(1, currentPage - 3);
    let end = Math.min(totalPages, currentPage + 3);
    
    if (start > 1) html += `<button class="page-btn" onclick="goToPage(1)">1</button>${start > 2 ? '<span style="color:#8b90a7;padding:5px;">...</span>' : ''}`;
    
    for (let i = start; i <= end; i++) {
      html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }
    
    if (end < totalPages) html += `${end < totalPages - 1 ? '<span style="color:#8b90a7;padding:5px;">...</span>' : ''}<button class="page-btn" onclick="goToPage(${totalPages})">${totalPages}</button>`;
    
    html += `<button class="page-btn" onclick="goToPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>다음</button>`;
    pag.innerHTML = html;
  }

  window.goToPage = function(p) {
    currentPage = p;
    renderTable();
    document.querySelector('.card').scrollIntoView({ behavior: 'smooth' });
  };

  // ── 렌더 ──
  function renderTable(keepScroll = false) {
    const q = document.getElementById('searchInput').value.trim().toLowerCase();
    let data = q ? ALL_JOBS.filter(j =>
      (j.company + j.title + j.requirements).toLowerCase().includes(q)
    ) : ALL_JOBS;
    
    if (showOnlyBookmarks) {
      data = data.filter(j => bookmarks.includes(j.link));
    }
    
    data = getSorted(data);

    const tbody = document.getElementById('tableBody');
    const empty = document.getElementById('emptyState');
    if (data.length === 0) {
      tbody.innerHTML = '';
      empty.style.display = 'block';
      document.getElementById('pagination').innerHTML = '';
    } else {
      const startIdx = (currentPage - 1) * PAGE_SIZE;
      const pageData = data.slice(startIdx, startIdx + PAGE_SIZE);
      
      // 스크롤 유지를 위해 html 변경 전 스크롤 위치 저장
      const scrollTop = window.scrollY;
      
      tbody.innerHTML = pageData.map((j, i) => makeRow(j, startIdx + i + 1)).join('');
      empty.style.display = 'none';
      renderPagination(data.length);
      
      if (keepScroll) {
        window.scrollTo(0, scrollTop);
      }
    }
    document.getElementById('visibleCount').textContent = data.length;
  }

  document.getElementById('searchInput').addEventListener('input', () => {
    currentPage = 1;
    renderTable();
  });
  renderTable();
</script>
</body>
</html>"""


def _detect_site(link: str) -> str:
    if 'saramin' in link:
        return '사람인'
    elif 'jobkorea' in link:
        return '잡코리아'
    elif 'wanted.co.kr' in link:
        return '원티드'
    elif 'linkareer' in link:
        return '링커리어'
    elif 'jumpit.co.kr' in link:
        return '점핏'
    return '기타'


def build_chart_data(postings: List[JobPosting], keywords: List[str]) -> dict:
    counts = [0] * len(keywords)
    for p in postings:
        text = (p.title + ' ' + p.requirements).lower()
        for i, kw in enumerate(keywords):
            if kw.lower() in text:
                counts[i] += 1
    return {'labels': keywords, 'counts': counts}


def generate_html(postings: List[JobPosting], keywords: List[str]) -> str:
    all_jobs = json.dumps([
        {
            'company':      html_module.escape(p.company),
            'title':        html_module.escape(p.title),
            'requirements': html_module.escape(p.requirements),
            'deadline':     html_module.escape(p.deadline),
            'link':         html_module.escape(p.link),
            'site':         _detect_site(p.link),
        }
        for p in postings
    ], ensure_ascii=False)

    chart_data = json.dumps(build_chart_data(postings, keywords), ensure_ascii=False)

    return (
        HTML_TEMPLATE
        .replace('__ALL_JOBS__', all_jobs)
        .replace('__CHART_DATA__', chart_data)
    )

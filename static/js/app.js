/**
 * app.js — Modular Frontend Client Library for CertPortal
 * Includes: REST API Client, Navigation Injector with Feather SVG Icons,
 * Chart.js Integration, AI Radial Integrity Gauge, Modal & Toast Controls.
 */

// ── SVG Icon Registry ──────────────────────────────────────────
const ICONS = {
  dashboard: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>`,
  insights: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>`,
  plus: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
  certificates: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
  gallery: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>`,
  notifications: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>`,
  broadcast: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"></path><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"></path><circle cx="12" cy="12" r="2"></circle><path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"></path><path d="M19.1 4.9C23 8.8 23 15.2 19.1 19.1"></path></svg>`,
  reviews: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>`,
  settings: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`,
  shield: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
  users: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
  userCheck: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="17 11 19 13 23 9"></polyline></svg>`,
  hod: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>`,
  bot: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>`,
  briefcase: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>`
};

// ── REST API Helper ─────────────────────────────────────────────
const API = {
  async get(url) {
    try {
      const res = await fetch(url);
      if (res.status === 401) { window.location.href = '/'; return null; }
      return await res.json();
    } catch (e) {
      console.error('API GET Error:', e);
      return null;
    }
  },
  async post(url, data) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (res.status === 401) { window.location.href = '/'; return null; }
      return await res.json();
    } catch (e) {
      console.error('API POST Error:', e);
      return null;
    }
  },
  async put(url, data) {
    try {
      const res = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (res.status === 401) { window.location.href = '/'; return null; }
      return await res.json();
    } catch (e) {
      console.error('API PUT Error:', e);
      return null;
    }
  },
  async delete(url) {
    try {
      const res = await fetch(url, { method: 'DELETE' });
      if (res.status === 401) { window.location.href = '/'; return null; }
      return await res.json();
    } catch (e) {
      console.error('API DELETE Error:', e);
      return null;
    }
  },
  async postForm(url, formData) {
    try {
      const res = await fetch(url, { method: 'POST', body: formData });
      if (res.status === 401) { window.location.href = '/'; return null; }
      return await res.json();
    } catch (e) {
      console.error('API Form Error:', e);
      return null;
    }
  }
};

// ── Toast Notifications ─────────────────────────────────────────
function showToast(message, type = 'success') {
  let stack = document.querySelector('.portal-toast-stack');
  if (!stack) {
    stack = document.createElement('div');
    stack.className = 'portal-toast-stack';
    document.body.appendChild(stack);
  }

  const toast = document.createElement('div');
  toast.className = `portal-toast portal-toast--${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span><span>${escapeHtml(message)}</span>`;
  stack.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

// ── Navigation Bar Builder ──────────────────────────────────────
function renderCampusHeader(user) {
  const initials = user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  let roleBadgeSubtitle = 'Student Workspace';
  if (user.role === 'admin' || user.role === 'hod') {
    roleBadgeSubtitle = 'HOD & Admin Console';
  } else if (user.role === 'staff') {
    roleBadgeSubtitle = 'Faculty Mentor Console';
  }

  let userMetaSubtitle = user.department || user.role;
  if (user.role === 'student') {
    userMetaSubtitle = `Year ${user.year || 1} • ${user.department || 'Engineering'}`;
  } else if (user.designation) {
    userMetaSubtitle = user.designation;
  }

  return `
    <header class="portal-header">
      <div class="portal-header__inner">
        <a href="/" class="portal-brand">
          <div class="portal-brand__logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
              <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
            </svg>
          </div>
          <div class="portal-brand__text">
            <span class="portal-brand__title">CertPortal</span>
            <span class="portal-brand__sub">${roleBadgeSubtitle}</span>
          </div>
        </a>

        <div class="portal-user-section">
          <div class="portal-user-meta">
            <span class="portal-user-meta__name">${escapeHtml(user.full_name)}</span>
            <span class="portal-user-meta__role">${escapeHtml(userMetaSubtitle)}</span>
          </div>
          <div class="portal-avatar-circle">${initials}</div>
        </div>
      </div>
    </header>
  `;
}

function renderSubNavBar(activePage, userRole) {
  const studentNav = [
    { href: '/student_dashboard.html', label: 'Overview', icon: ICONS.dashboard },
    { href: '/ai_assistant.html', label: 'AI Copilot', icon: ICONS.bot },
    { href: '/job_match.html', label: 'AI Job Matcher', icon: ICONS.briefcase },
    { href: '/ai_insights.html', label: 'Career Radar', icon: ICONS.insights },
    { href: '/add_certificate.html', label: 'Upload Credential', icon: ICONS.plus },
    { href: '/certificates.html', label: 'My Records', icon: ICONS.certificates },
    { href: '/gallery.html', label: 'Showcase', icon: ICONS.gallery },
    { href: '/notifications.html', label: 'Inbox', icon: ICONS.notifications },
    { href: '/settings.html', label: 'Settings', icon: ICONS.settings },
  ];

  const mentorNav = [
    { href: '/staff_dashboard.html', label: 'Mentor Overview & Mentees', icon: ICONS.dashboard },
    { href: '/staff_reviews.html', label: 'Verification Queue', icon: ICONS.reviews },
    { href: '/staff_notifications.html', label: 'Broadcast Center', icon: ICONS.broadcast },
    { href: '/certificates.html', label: 'Mentee Records', icon: ICONS.certificates },
    { href: '/settings.html', label: 'Account', icon: ICONS.settings },
  ];

  const hodNav = [
    { href: '/hod_management.html', label: 'HOD Management Console', icon: ICONS.hod },
    { href: '/staff_dashboard.html', label: 'Campus Analytics', icon: ICONS.dashboard },
    { href: '/staff_reviews.html', label: 'Verification Queue', icon: ICONS.reviews },
    { href: '/staff_notifications.html', label: 'Broadcast Center', icon: ICONS.broadcast },
    { href: '/certificates.html', label: 'All Records', icon: ICONS.certificates },
    { href: '/settings.html', label: 'Account', icon: ICONS.settings },
  ];

  let items = studentNav;
  if (userRole === 'admin' || userRole === 'hod') {
    items = hodNav;
  } else if (userRole === 'staff') {
    items = mentorNav;
  }

  const linksHtml = items.map(item => `
    <a href="${item.href}" class="portal-nav-item ${activePage === item.href ? 'is-active' : ''}">
      ${item.icon}
      <span>${item.label}</span>
    </a>
  `).join('');

  return `
    <nav class="portal-navbar">
      <div class="portal-navbar__inner">
        ${linksHtml}
      </div>
    </nav>
  `;
}

async function initPortal(activePage) {
  document.body.classList.add('portal-body');
  const user = await API.get('/api/auth/me');
  if (!user || user.error) {
    window.location.href = '/';
    return null;
  }

  const headerHtml = renderCampusHeader(user);
  const navHtml = renderSubNavBar(activePage, user.role);
  document.body.insertAdjacentHTML('afterbegin', headerHtml + navHtml);

  return user;
}

// ── Chart.js Builders ───────────────────────────────────────────
const THEME_COLORS = {
  brand: '#0d9488',
  brandDark: '#0f766e',
  accent: '#4f46e5',
  slate: '#64748b',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  border: '#e2e8f0'
};

function createLineChart(canvasId, labels, datasets) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: "'Inter', sans-serif", size: 12 } } }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: THEME_COLORS.border } },
        x: { grid: { display: false } }
      },
      elements: { line: { tension: 0.35 } }
    }
  });
}

function createDoughnutChart(canvasId, labels, data, colors) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } }
      }
    }
  });
}

function createBarChart(canvasId, labels, data, colors) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors || THEME_COLORS.brand, borderRadius: 5, maxBarThickness: 36 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: THEME_COLORS.border } },
        x: { grid: { display: false } }
      }
    }
  });
}

function createRadarChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'radar',
    data: {
      labels,
      datasets: [{
        label: 'Domain Match Index (%)',
        data,
        backgroundColor: 'rgba(13, 148, 136, 0.15)',
        borderColor: THEME_COLORS.brand,
        borderWidth: 2,
        pointBackgroundColor: THEME_COLORS.brand,
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 25, backdropColor: 'transparent', font: { size: 10 } },
          grid: { color: THEME_COLORS.border }
        }
      }
    }
  });
}

function createHorizontalBarChart(canvasId, labels, data, colors) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors || THEME_COLORS.brand, borderRadius: 4, maxBarThickness: 20 }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, grid: { color: THEME_COLORS.border } },
        y: { grid: { display: false } }
      }
    }
  });
}

// ── AI Radial Integrity Dial ───────────────────────────────────
function renderIntegrityGauge(containerId, score, riskLevel, riskColor) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const radius = 68;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  container.innerHTML = `
    <div class="integrity-dial-container">
      <div class="integrity-radial-gauge">
        <svg class="integrity-radial-gauge__svg" viewBox="0 0 170 170">
          <circle class="integrity-radial-gauge__bg" cx="85" cy="85" r="${radius}" />
          <circle class="integrity-radial-gauge__fill" cx="85" cy="85" r="${radius}"
            stroke="${riskColor}"
            stroke-dasharray="${circumference}"
            stroke-dashoffset="${circumference}" />
        </svg>
        <div class="integrity-radial-gauge__center">
          <div class="integrity-radial-gauge__number">${score}</div>
          <div class="integrity-radial-gauge__label">Index Score</div>
        </div>
      </div>
      <div style="margin-top: 10px;">
        <span class="portal-badge portal-badge--risk-${riskLevel.toLowerCase()}">${riskLevel} Integrity Risk</span>
      </div>
    </div>
  `;

  requestAnimationFrame(() => {
    const fill = container.querySelector('.integrity-radial-gauge__fill');
    if (fill) fill.style.strokeDashoffset = offset;
  });
}

function renderDimensionBars(containerId, dimensions) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const labels = {
    metadata_consistency: 'Metadata Integrity',
    skill_relevancy: 'Taxonomy Match',
    issuer_trust: 'Issuer Trust Level',
    temporal_validity: 'Temporal Validity',
    content_authenticity: 'Artifact Evidence'
  };

  const getMeterColor = (pct) => {
    if (pct >= 80) return '#10b981';
    if (pct >= 60) return '#f59e0b';
    return '#ef4444';
  };

  container.innerHTML = Object.entries(dimensions).map(([key, dim]) => `
    <div class="integrity-meter">
      <div class="integrity-meter__header">
        <span>${labels[key] || key}</span>
        <span>${dim.score}/${dim.max}</span>
      </div>
      <div class="integrity-meter__track">
        <div class="integrity-meter__bar" style="width: 0%; background: ${getMeterColor(dim.pct)}" data-pct="${dim.pct}"></div>
      </div>
    </div>
  `).join('');

  setTimeout(() => {
    container.querySelectorAll('.integrity-meter__bar').forEach(bar => {
      bar.style.width = `${bar.dataset.pct}%`;
    });
  }, 100);
}

// ── Modals & Utilities ──────────────────────────────────────────
function openPortalModal(title, bodyHtml, footerHtml = '') {
  let overlay = document.querySelector('.portal-modal-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'portal-modal-overlay';
    document.body.appendChild(overlay);
  }

  overlay.innerHTML = `
    <div class="portal-modal-dialog">
      <div class="portal-modal-header">
        <div class="portal-modal-title">${escapeHtml(title)}</div>
        <button class="portal-modal-close" onclick="closePortalModal()">&times;</button>
      </div>
      <div class="portal-modal-body">${bodyHtml}</div>
      ${footerHtml ? `<div class="portal-modal-footer">${footerHtml}</div>` : ''}
    </div>
  `;

  overlay.onclick = (e) => { if (e.target === overlay) closePortalModal(); };
  requestAnimationFrame(() => overlay.classList.add('is-active'));
}

function closePortalModal() {
  const overlay = document.querySelector('.portal-modal-overlay');
  if (overlay) {
    overlay.classList.remove('is-active');
    setTimeout(() => overlay.remove(), 250);
  }
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

function getStatusBadge(status) {
  const s = (status || 'pending').toLowerCase();
  return `<span class="portal-badge portal-badge--${s}">${s}</span>`;
}

function getIntegrityRiskBadge(score) {
  if (score <= 0) return '<span class="portal-badge portal-badge--neutral">Not Evaluated</span>';
  if (score >= 85) return `<span class="portal-badge portal-badge--risk-low">${score}/100</span>`;
  if (score >= 65) return `<span class="portal-badge portal-badge--risk-medium">${score}/100</span>`;
  if (score >= 40) return `<span class="portal-badge portal-badge--risk-high">${score}/100</span>`;
  return `<span class="portal-badge portal-badge--risk-critical">${score}/100</span>`;
}

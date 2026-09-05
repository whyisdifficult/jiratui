/*  STATE  */
let isDark = true,
    currentUser = null;
let chatHistory = [];

/*  THEME  */
function toggleTheme() {
    isDark = !isDark;
    document.getElementById('htmlRoot').classList.toggle('lm', !isDark);
    // Landing icons
    const si = document.getElementById('suni'),
        mi = document.getElementById('mooni');
    if (si) {
        si.style.display = isDark ? 'none' : 'inline';
        mi.style.display = isDark ? 'inline' : 'none';
    }
    // Update charts
    updateChartColors();
}
document.getElementById('thbtn').addEventListener('click', toggleTheme);

/*  NAVBAR  */
window.addEventListener('scroll', () => document.getElementById('nbar').classList.toggle('scr', scrollY > 40));
let mbOpen = false;
document.getElementById('mbtog').addEventListener('click', () => {
    mbOpen = !mbOpen;
    document.getElementById('mbmenu').classList.toggle('open', mbOpen);
    document.getElementById('barIcon').style.display = mbOpen ? 'none' : 'inline';
    document.getElementById('xIcon').style.display = mbOpen ? 'inline' : 'none';
});
document.querySelectorAll('#mbmenu a, #mbmenu button').forEach(el =>
    el.addEventListener('click', () => {
        mbOpen = false;
        document.getElementById('mbmenu').classList.remove('open');
        document.getElementById('barIcon').style.display = 'inline';
        document.getElementById('xIcon').style.display = 'none';
    })
);

/*  REVEAL  */
const rvObs = new IntersectionObserver(
    entries => entries.forEach(e => {
        if (e.isIntersecting) e.target.classList.add('in');
    }), {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    }
);
document.querySelectorAll('.rv').forEach(el => rvObs.observe(el));

/*  DASHBOARD NAVIGATION  */
function dbNav(section, btn) {
    document.querySelectorAll('.db-nl').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.db-section').forEach(s => s.classList.remove('active'));
    if (btn) btn.classList.add('active');
    // find the correct sidebar button if btn not provided
    if (!btn) {
        document.querySelectorAll('.db-nl').forEach(b => {
            if (b.getAttribute('onclick') && b.getAttribute('onclick').includes("'" + section + "'")) b.classList.add('active');
        });
    }
    const sec = document.getElementById('sec-' + section);
    if (sec) {
        sec.classList.add('active');
        sec.style.animation = 'fadeIn .4s ease';
    }
}

/*  CHARTS  */
let ovChartInst = null,
    anChartInst = null;

function chartColors() {
    return {
        grid: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.06)',
        ticks: isDark ? '#6b6b8a' : '#7878a0'
    };
}

function updateChartColors() {
    [ovChartInst, anChartInst].forEach(ch => {
        if (!ch) return;
        const {
            grid,
            ticks
        } = chartColors();
        ch.options.scales.x.grid.color = grid;
        ch.options.scales.x.ticks.color = ticks;
        ch.options.scales.y.grid.color = grid;
        ch.options.scales.y.ticks.color = ticks;
        if (ch.options.plugins.legend) ch.options.plugins.legend.labels.color = isDark ? '#a8a8c8' : '#3d3d5c';
        ch.update();
    });
}

function escapeHtml(t) {
    return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* Close dropdowns on outside click */
document.addEventListener('click', (e) => {
    if (!document.getElementById('notifWrap')?.contains(e.target))
        document.getElementById('notifDropdown')?.classList.remove('open');
    if (!document.getElementById('profileWrap')?.contains(e.target)) {
        document.getElementById('profileDropdown')?.classList.remove('open');
        const ch = document.getElementById('profileChevron');
        if (ch) ch.style.transform = 'rotate(0deg)';
    }
});

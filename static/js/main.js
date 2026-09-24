// Main JavaScript - Brightlant Webmail Notification & UI Engine
document.addEventListener('DOMContentLoaded', function () {
    // Theme Switcher Initialization
    let storedTheme = localStorage.getItem('theme') || 'light';
    let currentTheme = storedTheme;
    if (storedTheme === 'system') {
        currentTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    // Color palette Initialization (accent theme, works in light & dark)
    let storedPalette = localStorage.getItem('palette') || 'ocean';
    document.documentElement.setAttribute('data-palette', storedPalette);

    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            let activeTheme = document.documentElement.getAttribute('data-theme');
            let newTheme = activeTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        const icon = document.getElementById('themeToggleIcon');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun text-warning';
            } else {
                icon.className = 'fas fa-moon text-secondary';
            }
        }
    }

    // Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    if (sidebarCollapse && sidebar) {
        sidebarCollapse.addEventListener('click', function () {
            sidebar.classList.toggle('expanded');
            if (sidebarBackdrop) {
                sidebarBackdrop.classList.toggle('show', sidebar.classList.contains('expanded'));
            }
        });
    }
    // Tapping the backdrop closes the mobile sidebar
    if (sidebarBackdrop && sidebar) {
        sidebarBackdrop.addEventListener('click', function () {
            sidebar.classList.remove('expanded');
            sidebarBackdrop.classList.remove('show');
        });
    }

    // Sidebar Active Link Auto-Highlighting
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(function (link) {
        const linkPath = link.getAttribute('href');
        if (linkPath && (linkPath === currentPath || (currentPath !== '/' && linkPath !== '/' && currentPath.startsWith(linkPath)))) {
            link.classList.add('active-link');
        }
    });

    // Auto Dismiss Flash Alerts after 5s
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch(e) {}
        }, 5000);
    });

    // Initialize Real-Time Notification Engine if logged in
    initNotificationEngine();

    // PWA Service Worker Registration
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(err => console.log('PWA SW Register Error:', err));
    }
});

// PWA Deferred Installation Prompt Handler
let deferredPwaPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPwaPrompt = e;
    const btn = document.getElementById('pwaInstallBtn');
    if (btn) btn.style.display = 'inline-flex';
});

function installPwaApp() {
    if (deferredPwaPrompt) {
        deferredPwaPrompt.prompt();
        deferredPwaPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted PWA installation');
                const btn = document.getElementById('pwaInstallBtn');
                if (btn) btn.style.display = 'none';
            }
            deferredPwaPrompt = null;
        });
    } else {
        alert("App Installation: To install Brightlant Webmail, click the install icon in your browser URL address bar!");
    }
}

// --- AUDIO NOTIFICATION SYNTHESIZER (Web Audio API) — 5 device-style tones ---
const NOTIF_DEFAULTS = { sound: 'shimmer', soundOn: true, volume: 0.6, desktop: true, toast: true };

function getNotifPrefs() {
    try {
        return Object.assign({}, NOTIF_DEFAULTS, JSON.parse(localStorage.getItem('brightlantNotifPrefs') || '{}'));
    } catch (e) {
        return Object.assign({}, NOTIF_DEFAULTS);
    }
}
function saveNotifPrefs(p) {
    localStorage.setItem('brightlantNotifPrefs', JSON.stringify(Object.assign(getNotifPrefs(), p)));
}

// Card metadata used by the settings page (label + icon)
const NOTIF_SOUNDS = {
    shimmer:  { label: 'Shimmer',   icon: 'star' },
    droplet:  { label: 'Droplet',   icon: 'droplet' },
    ascend:   { label: 'Bloom',     icon: 'arrow-trend-up' },
    dingdong: { label: 'Doorbell',  icon: 'bell' },
    pop:      { label: 'Bubble',    icon: 'comment-dots' }
};

let _notifCtx = null;

// Play one pitched note with harmonic partials + a pluck/mallet envelope.
function _note(ctx, out, freq, start, dur, opts) {
    opts = opts || {};
    const type = opts.type || 'sine';
    const peak = (opts.gain != null ? opts.gain : 0.9);
    const partials = opts.partials || [[1, 1], [2, 0.3], [3, 0.1]];
    const t0 = ctx.currentTime + start;
    partials.forEach(function (p) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq * p[0], t0);
        if (opts.slideTo) osc.frequency.exponentialRampToValueAtTime(opts.slideTo * p[0], t0 + dur);
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(Math.max(0.0002, peak * p[1]), t0 + (opts.attack || 0.008));
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
        osc.connect(g); g.connect(out);
        osc.start(t0); osc.stop(t0 + dur + 0.04);
    });
}

// Recipes: each receives a note(freq, start, dur, opts) shortcut.
// Tuned to be soft, warm and pleasant — gentle attacks + consonant intervals.
const SOUND_RECIPES = {
    // Soft glassy bell chime with a long shimmering tail (iOS-like)
    shimmer: function (n) {
        n(1046.50, 0.00, 0.90, { attack: 0.005, gain: 0.8, partials: [[1,1],[2,0.35],[3,0.12],[4.2,0.06]] });
        n(1567.98, 0.07, 0.95, { attack: 0.005, gain: 0.6, partials: [[1,1],[2,0.3],[3,0.1]] });
        n(2093.00, 0.15, 1.05, { attack: 0.006, gain: 0.35, partials: [[1,1],[2,0.2]] });
    },
    // Gentle water droplet: a soft downward blip then a light high ping
    droplet: function (n) {
        n(1318.51, 0.00, 0.20, { type: 'sine', gain: 0.8, attack: 0.004, slideTo: 880.00, partials: [[1,1],[2,0.15]] });
        n(1975.53, 0.13, 0.45, { type: 'sine', gain: 0.4, attack: 0.005, partials: [[1,1],[2,0.12]] });
    },
    // Warm rising major arpeggio (C–E–G) with a soft mallet tone
    ascend: function (n) {
        n(1046.50, 0.00, 0.42, { type: 'triangle', gain: 0.75, attack: 0.006, partials: [[1,1],[2,0.35],[4,0.12]] });
        n(1318.51, 0.11, 0.44, { type: 'triangle', gain: 0.75, attack: 0.006, partials: [[1,1],[2,0.35],[4,0.12]] });
        n(1567.98, 0.22, 0.66, { type: 'triangle', gain: 0.8,  attack: 0.006, partials: [[1,1],[2,0.3],[4,0.1]] });
    },
    // Classic warm two-tone doorbell (ding–dong, E→C)
    dingdong: function (n) {
        n(1318.51, 0.00, 0.55, { type: 'sine', gain: 0.85, attack: 0.006, partials: [[1,1],[2,0.28],[3,0.08]] });
        n(1046.50, 0.30, 0.85, { type: 'sine', gain: 0.85, attack: 0.006, partials: [[1,1],[2,0.28],[3,0.08]] });
    },
    // Playful messaging bubble pops (two quick upward blips)
    pop: function (n) {
        n(587.33, 0.00, 0.13, { type: 'sine', gain: 0.8, attack: 0.003, slideTo: 880.00, partials: [[1,1],[2,0.1]] });
        n(880.00, 0.10, 0.16, { type: 'sine', gain: 0.8, attack: 0.003, slideTo: 1174.66, partials: [[1,1],[2,0.1]] });
    }
};

function playNotifSound(name, volume) {
    const vol = (typeof volume === 'number') ? volume : getNotifPrefs().volume;
    try {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        _notifCtx = _notifCtx || new AC();
        const ctx = _notifCtx;
        if (ctx.state === 'suspended') ctx.resume();

        const master = ctx.createGain();
        master.gain.value = Math.max(0.0001, vol) * 0.45;

        // Warmth: gentle low-pass to remove harsh high frequencies
        const warmth = ctx.createBiquadFilter();
        warmth.type = 'lowpass';
        warmth.frequency.value = 6500;
        warmth.Q.value = 0.5;

        master.connect(warmth);
        warmth.connect(ctx.destination);

        const recipe = SOUND_RECIPES[name] || SOUND_RECIPES[NOTIF_DEFAULTS.sound] || SOUND_RECIPES.shimmer;
        recipe(function (f, s, d, o) { _note(ctx, master, f, s, d, o); });
    } catch (e) {
        console.log("Audio notification play error:", e);
    }
}
// Backward-compatible entry point used by the live inbox engine
function playNotificationSound() {
    const p = getNotifPrefs();
    if (!p.soundOn) return;
    playNotifSound(p.sound, p.volume);
}
// Expose for the settings page preview buttons
window.playNotifSound = playNotifSound;
window.NOTIF_SOUNDS = NOTIF_SOUNDS;
window.getNotifPrefs = getNotifPrefs;
window.saveNotifPrefs = saveNotifPrefs;


// --- REAL-TIME LIVE INBOX NOTIFICATION ENGINE ---
let previousUnreadCount = null;
let lastKnownMsgId = null;

function initNotificationEngine() {
    const badgeEl = document.getElementById('notificationBadge');
    if (!badgeEl) return; // Not logged in or top navbar not present

    // Request Browser Notification Permission silently
    if ("Notification" in window && Notification.permission === "default") {
        document.addEventListener('click', function requestOnce() {
            Notification.requestPermission();
            document.removeEventListener('click', requestOnce);
        }, { once: true });
    }

    // Poll every 6 seconds for unread emails and status changes
    pollUnreadStatus();
    setInterval(pollUnreadStatus, 6000);

    // Load recent notifications into the bell dropdown (and refresh when opened)
    loadRecentNotifications();
    const bell = document.getElementById('notifBellBtn');
    if (bell) bell.addEventListener('click', loadRecentNotifications);
}

function pollUnreadStatus() {
    fetch('/api/notifications/unread')
    .then(res => {
        if (!res.ok) throw new Error('Unauthenticated');
        return res.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const currentCount = data.unread_count;
            const badgeEl = document.getElementById('notificationBadge');
            const navTextBadge = document.getElementById('navInboxBadge');
            const sidebarNotifCount = document.getElementById('sidebarNotifCount');

            if (badgeEl) {
                if (currentCount > 0) {
                    badgeEl.innerText = currentCount;
                    badgeEl.style.display = 'inline-block';
                } else {
                    badgeEl.style.display = 'none';
                }
            }

            // Sidebar Notifications count pill
            if (sidebarNotifCount) {
                if (currentCount > 0) {
                    sidebarNotifCount.innerText = currentCount > 99 ? '99+' : currentCount;
                    sidebarNotifCount.classList.remove('d-none');
                } else {
                    sidebarNotifCount.classList.add('d-none');
                }
            }

            if (navTextBadge) {
                navTextBadge.innerText = currentCount > 0 ? `${currentCount} Unread` : 'Inbox';
            }

            // Document Title Update
            const baseTitle = "Brightlant Webmail";
            if (currentCount > 0) {
                document.title = `(${currentCount}) Inbox - ${baseTitle}`;
            } else {
                document.title = baseTitle;
            }

            // Check if new incoming email arrived
            if (data.latest_msg && previousUnreadCount !== null) {
                if (currentCount > previousUnreadCount || (data.latest_msg.id !== lastKnownMsgId && !data.latest_msg.is_read)) {
                    triggerNewEmailNotification(data.latest_msg);
                }
            }

            previousUnreadCount = currentCount;
            if (data.latest_msg) {
                lastKnownMsgId = data.latest_msg.id;
            }
        }
    })
    .catch(err => {
        // Silently ignore when logged out or offline
    });
}

function triggerNewEmailNotification(msg) {
    const prefs = getNotifPrefs();

    // 1. Play Sound (respects chosen tone + on/off + volume)
    playNotificationSound();

    // 2. Show In-App Floating Toast Alert
    if (prefs.toast) showNotificationToast(msg);

    // 3. Show Browser Desktop Notification if enabled
    if (prefs.desktop && "Notification" in window && Notification.permission === "granted") {
        try {
            const notif = new Notification(`📩 New Mail from ${msg.sender_name}`, {
                body: msg.subject,
                icon: '/static/images/logo.png'
            });
            notif.onclick = function() {
                window.focus();
                window.location.href = `/mail/${msg.id}`;
            };
        } catch(e) {}
    }
}

function showNotificationToast(msg) {
    let container = document.getElementById('liveToastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'liveToastContainer';
        container.style.cssText = 'position: fixed; top: 70px; right: 12px; left: auto; z-index: 9999; width: min(380px, calc(100vw - 24px));';
        document.body.appendChild(container);
    }

    const toastHtml = `
        <div class="toast show rounded-4 border-0 shadow-lg bg-white overflow-hidden mb-2 animate-bounce" role="alert">
            <div class="toast-header bg-primary text-white border-0 py-2">
                <i class="fas fa-envelope-open-text me-2"></i>
                <strong class="me-auto font-sans" style="font-size: 13px;">New Webmail Received</strong>
                <small class="text-white-50">${msg.created_at || 'Just now'}</small>
                <button type="button" class="btn-close btn-close-white ms-2" onclick="this.closest('.toast').remove()"></button>
            </div>
            <div class="toast-body p-3 bg-light cursor-pointer" onclick="window.location.href='/mail/${msg.id}'">
                <div class="fw-bold text-dark text-truncate" style="font-size: 13px;">From: ${msg.sender_name} &lt;${msg.sender_email}&gt;</div>
                <div class="text-secondary text-truncate mt-1" style="font-size: 12px;">${msg.subject}</div>
                <div class="mt-2 text-primary font-mono fw-bold" style="font-size: 11px;">Click to view message &rarr;</div>
            </div>
        </div>
    `;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = toastHtml;
    const toastNode = wrapper.firstElementChild;
    container.appendChild(toastNode);

    setTimeout(() => {
        if (toastNode && toastNode.parentNode) {
            toastNode.remove();
        }
    }, 8000);
}

// --- Populate the bell dropdown with recent notifications ---
function loadRecentNotifications() {
    const box = document.getElementById('notifDropdownContent');
    if (!box) return;
    fetch('/api/notifications/recent')
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(data => {
            if (data.status !== 'success' || !data.messages || !data.messages.length) return;
            box.innerHTML = data.messages.map(m => `
                <a href="/mail/${m.id}" class="d-flex align-items-start gap-2 px-3 py-2 text-decoration-none"
                   style="border-bottom:1px solid var(--border); ${m.is_read ? '' : 'background:var(--surface-2);'}">
                    <div style="width:34px;height:34px;border-radius:9px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;color:#fff;background:var(--accent);">
                        ${(m.sender_name || 'BR').substring(0,2).toUpperCase()}
                    </div>
                    <div style="min-width:0;flex:1;">
                        <div class="fw-700 text-truncate" style="font-size:12.5px;color:var(--text-900);">${m.sender_name || 'Brightlant'}</div>
                        <div class="text-truncate" style="font-size:11.5px;color:var(--text-500);">${m.subject || ''}</div>
                        <div style="font-size:10.5px;color:var(--text-400);">${m.created_at}</div>
                    </div>
                    ${m.is_read ? '' : '<span style="width:8px;height:8px;border-radius:50%;background:var(--accent);flex-shrink:0;margin-top:5px;"></span>'}
                </a>`).join('');
        })
        .catch(() => {});
}

// AI Email Generator Function for Composer
function triggerAiGenerator(promptInputId, toneSelectId, editorId, subjectInputId) {
    const prompt = document.getElementById(promptInputId) ? document.getElementById(promptInputId).value : '';
    const tone = document.getElementById(toneSelectId) ? document.getElementById(toneSelectId).value : 'professional';

    if (!prompt) {
        alert("Please enter a short prompt topic for AI Copilot (e.g. 'Festival discount offer')!");
        return;
    }

    const aiBtn = event.currentTarget;
    const origHtml = aiBtn.innerHTML;
    aiBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> AI Generating...';
    aiBtn.disabled = true;

    fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt, tone: tone })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            if (subjectInputId && document.getElementById(subjectInputId)) {
                document.getElementById(subjectInputId).value = data.subject;
            }
            if (editorId && document.getElementById(editorId)) {
                document.getElementById(editorId).value = data.content;
            }
        }
        aiBtn.innerHTML = origHtml;
        aiBtn.disabled = false;
    })
    .catch(err => {
        console.error("AI Error:", err);
        aiBtn.innerHTML = origHtml;
        aiBtn.disabled = false;
    });
}

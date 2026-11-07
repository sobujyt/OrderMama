(function () {
  var cfg = document.getElementById('cfg').dataset;
  var box = document.getElementById('orders'), empty = document.getElementById('empty'), soundBtn = document.getElementById('soundBtn');
  var NEXT = { pending: ['preparing', 'accept'], preparing: ['ready', 'mark_ready'], ready: ['served', 'mark_served'] };
  var orders = [], lastMax = null, ctx = null, soundOn = false, baseTitle = document.title, fresh = {};

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function beep() {
    if (!ctx) return;
    [0, 0.25, 0.5].forEach(function (d) {
      var o = ctx.createOscillator(), g = ctx.createGain(), t = ctx.currentTime + d;
      o.frequency.value = 880; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.25, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
      o.start(t); o.stop(t + 0.2);
    });
  }

  function card(o) {
    var n = NEXT[o.status];
    return '<article class="card order st-' + o.status + (fresh[o.id] ? ' fresh' : '') + '">' +
      '<header><b>#' + o.id + '</b><span class="badge ' + o.status + '">' + esc(OM.t('st_' + o.status)) + '</span><small>' + o.time + '</small></header>' +
      '<p>' + (o.table ? esc(OM.t('table')) + ' <b>' + o.table + '</b> · ' : '') + esc(o.name) + (o.phone ? ' · ' + esc(o.phone) : '') + '</p>' +
      '<ul>' + o.items.map(function (i) { return '<li>' + i.qty + ' × ' + esc(i.name) + '</li>'; }).join('') + '</ul>' +
      (o.note ? '<p class="note">📝 ' + esc(o.note) + '</p>' : '') +
      '<footer><b>' + OM.money(o.total) + '</b><span class="acts">' +
      '<button class="btn sm danger" data-id="' + o.id + '" data-s="cancelled">' + esc(OM.t('cancel')) + '</button>' +
      (n ? '<button class="btn sm" data-id="' + o.id + '" data-s="' + n[0] + '">' + esc(OM.t(n[1])) + '</button>' : '') +
      '</span></footer></article>';
  }

  function render() {
    box.innerHTML = orders.map(card).join('');
    empty.hidden = orders.length > 0;
    if (soundOn) soundBtn.textContent = '🔔 ' + OM.t('sound_enabled');
  }

  function poll() {
    fetch(cfg.api, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok || r.redirected) { location.reload(); throw new Error('auth'); }
      return r.json();
    }).then(function (d) {
      orders = d.orders;
      var pend = orders.filter(function (o) { return o.status === 'pending'; }).map(function (o) { return o.id; });
      var max = pend.length ? Math.max.apply(null, pend) : 0;
      if (lastMax !== null && max > lastMax) {
        orders.forEach(function (o) { if (o.status === 'pending' && o.id > lastMax) fresh[o.id] = true; });
        if (soundOn) beep();
        document.title = '🔔 ' + OM.t('new_order');
      }
      lastMax = Math.max(lastMax || 0, max);
      render();
    }).catch(function () { }).then(function () { setTimeout(poll, 5000); });
  }

  soundBtn.addEventListener('click', function () {
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    ctx.resume(); soundOn = true; beep(); render();
  });
  window.addEventListener('focus', function () { document.title = baseTitle; fresh = {}; });

  box.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-s]'); if (!b) return;
    if (b.dataset.s === 'cancelled' && !confirm(OM.t('confirm'))) return;
    b.disabled = true;
    fetch(cfg.statusUrl.replace('/0/', '/' + b.dataset.id + '/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': OM.csrf() },
      body: 'status=' + encodeURIComponent(b.dataset.s)
    }).then(function () { return fetch(cfg.api, { credentials: 'same-origin' }); })
      .then(function (r) { return r.json(); })
      .then(function (d) { orders = d.orders; render(); })
      .catch(function () { b.disabled = false; });
  });

  OM.onLang.push(render);
  render(); poll();
})();

(function () {
  var cfg = document.getElementById('cfg').dataset;
  var KEY = 'om_cart_' + cfg.slug;
  var items = {}, cart = {};
  document.querySelectorAll('.item').forEach(function (el) {
    items[el.dataset.id] = { price: parseFloat(el.dataset.price), en: el.dataset.nameEn, bn: el.dataset.nameBn || el.dataset.nameEn, el: el };
  });
  try { cart = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { cart = {}; }
  Object.keys(cart).forEach(function (id) { if (!items[id] || !(cart[id] > 0)) delete cart[id]; });

  var $ = function (id) { return document.getElementById(id); };
  var bar = $('cartBar'), drawer = $('drawer'), nameEl = $('fName'), phoneEl = $('fPhone'), noteEl = $('fNote'), errEl = $('fErr'), btn = $('fSubmit');
  nameEl.value = localStorage.getItem('om_name') || ''; phoneEl.value = localStorage.getItem('om_phone') || '';

  function count() { return Object.keys(cart).reduce(function (s, id) { return s + cart[id]; }, 0); }
  function total() { return Object.keys(cart).reduce(function (s, id) { return s + items[id].price * cart[id]; }, 0); }
  function nm(id) { return OM.lang === 'bn' ? items[id].bn : items[id].en; }
  function save() { localStorage.setItem(KEY, JSON.stringify(cart)); render(); }

  function stepper(id) {
    var q = cart[id] || 0;
    return q ? '<span class="stepper"><button type="button" data-act="dec" data-id="' + id + '">−</button><b>' + OM.num(q) + '</b><button type="button" data-act="inc" data-id="' + id + '">+</button></span>'
             : '<button type="button" class="btn sm" data-act="inc" data-id="' + id + '">+ ' + OM.t('add') + '</button>';
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function render() {
    Object.keys(items).forEach(function (id) { items[id].el.querySelector('.act').innerHTML = stepper(id); });
    var n = count();
    bar.hidden = n === 0;
    $('cartCount').textContent = OM.t('view_order') + ' (' + OM.num(n) + ')';
    $('cartTotal').textContent = OM.money(total());
    $('cartSum').textContent = OM.money(total());
    var ids = Object.keys(cart);
    $('cartList').innerHTML = ids.length ? ids.map(function (id) {
      return '<div class="cline"><span>' + esc(nm(id)) + '<br><small class="muted">' + OM.money(items[id].price) + '</small></span>' + stepper(id) + '<b>' + OM.money(items[id].price * cart[id]) + '</b></div>';
    }).join('') : '<p class="muted center">' + OM.t('empty') + '</p>';
    if (!n && !drawer.hidden) drawer.hidden = true;
  }

  function submit() {
    var name = nameEl.value.trim();
    errEl.textContent = '';
    if (!name) { errEl.textContent = OM.t('name_required'); nameEl.focus(); return; }
    if (!count()) { errEl.textContent = OM.t('empty_cart'); return; }
    btn.disabled = true; btn.textContent = OM.t('placing');
    fetch(cfg.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': OM.csrf() },
      body: JSON.stringify({
        name: name, phone: phoneEl.value.trim(), note: noteEl.value.trim(), table: cfg.table,
        items: Object.keys(cart).map(function (id) { return { id: id, qty: cart[id] }; })
      })
    }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.d.error || 'bad_request');
        localStorage.setItem('om_name', name); localStorage.setItem('om_phone', phoneEl.value.trim());
        localStorage.removeItem(KEY);
        location.href = res.d.url;
      })
      .catch(function (e) {
        errEl.textContent = OM.t(e.message) || OM.t('bad_request');
        btn.disabled = false; btn.textContent = OM.t('place_order');
      });
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-act]'); if (!b) return;
    var id = b.dataset.id, act = b.dataset.act;
    if (act === 'inc') { cart[id] = Math.min((cart[id] || 0) + 1, 50); save(); }
    else if (act === 'dec') { cart[id] = (cart[id] || 0) - 1; if (cart[id] <= 0) delete cart[id]; save(); }
    else if (act === 'open') drawer.hidden = false;
    else if (act === 'close') drawer.hidden = true;
    else if (act === 'submit') submit();
  });
  drawer.addEventListener('click', function (e) { if (e.target === drawer) drawer.hidden = true; });

  OM.onLang.push(render);
  render();
})();

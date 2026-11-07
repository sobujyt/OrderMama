(function () {
  var I18N = {
    en: {
      menu: 'Menu', add: 'Add', view_order: 'View order', your_order: 'Your order', total: 'Total', empty: 'Your order is empty',
      your_name: 'Your name', phone_opt: 'Phone (optional)', note_opt: 'Note (optional)', place_order: 'Place order', placing: 'Placing order…',
      name_required: 'Please enter your name', empty_cart: 'Please add at least one item', bad_request: 'Something went wrong. Try again.',
      table: 'Table', order: 'Order', no_items: 'No items yet', back: 'Back to menu',
      step_pending: 'Placed', step_preparing: 'Preparing', step_ready: 'Ready', step_served: 'Served',
      st_pending: 'Waiting for the restaurant to accept', st_preparing: 'Being prepared', st_ready: 'Ready!', st_served: 'Served. Enjoy your meal!', st_cancelled: 'Cancelled',
      live_orders: 'Live orders', history: 'History', menu_manage: 'Menu', tables: 'Tables', settings: 'Settings', logout: 'Logout', login: 'Login', dashboard: 'Dashboard',
      no_orders: 'No active orders', accept: 'Accept', mark_ready: 'Mark ready', mark_served: 'Mark served', cancel: 'Cancel', confirm: 'Are you sure?',
      sound_on: 'Enable sound alert', sound_enabled: 'Sound alert on', new_order: 'New order!', save: 'Save', add_category: 'Add category', add_item: 'Add item',
      edit: 'Edit', delete: 'Delete', print: 'Print', add_tables: 'Add tables', menu_qr: 'Menu QR (no table)', open_menu: 'Open menu',
      restaurants: 'Restaurants', create_restaurant: 'Create restaurant', active: 'Active', inactive: 'Inactive', activate: 'Activate', deactivate: 'Deactivate',
      today_sales: "Today's sales (served)", orders: 'Orders', available: 'Available', unavailable: 'Hidden', home_tag: 'QR menu & ordering for restaurants',
      stats_rest: 'Restaurants', stats_active: 'Active', stats_orders: 'Total orders', stats_today: 'Orders today'
    },
    bn: {
      menu: 'মেনু', add: 'যোগ করুন', view_order: 'অর্ডার দেখুন', your_order: 'আপনার অর্ডার', total: 'মোট', empty: 'আপনার অর্ডার খালি',
      your_name: 'আপনার নাম', phone_opt: 'ফোন নম্বর (ঐচ্ছিক)', note_opt: 'নোট (ঐচ্ছিক)', place_order: 'অর্ডার করুন', placing: 'অর্ডার হচ্ছে…',
      name_required: 'অনুগ্রহ করে আপনার নাম লিখুন', empty_cart: 'অন্তত একটি আইটেম যোগ করুন', bad_request: 'কিছু ভুল হয়েছে। আবার চেষ্টা করুন।',
      table: 'টেবিল', order: 'অর্ডার', no_items: 'এখনো কোনো আইটেম নেই', back: 'মেনুতে ফিরুন',
      step_pending: 'অর্ডার হয়েছে', step_preparing: 'তৈরি হচ্ছে', step_ready: 'তৈরি', step_served: 'পরিবেশিত',
      st_pending: 'রেস্টুরেন্টের গ্রহণের অপেক্ষায়', st_preparing: 'আপনার খাবার তৈরি হচ্ছে', st_ready: 'খাবার তৈরি!', st_served: 'পরিবেশন করা হয়েছে। খাবার উপভোগ করুন!', st_cancelled: 'অর্ডার বাতিল হয়েছে',
      live_orders: 'লাইভ অর্ডার', history: 'ইতিহাস', menu_manage: 'মেনু', tables: 'টেবিল', settings: 'সেটিংস', logout: 'লগআউট', login: 'লগইন', dashboard: 'ড্যাশবোর্ড',
      no_orders: 'কোনো সক্রিয় অর্ডার নেই', accept: 'গ্রহণ করুন', mark_ready: 'তৈরি হয়েছে', mark_served: 'পরিবেশিত', cancel: 'বাতিল', confirm: 'আপনি কি নিশ্চিত?',
      sound_on: 'সাউন্ড অ্যালার্ট চালু করুন', sound_enabled: 'সাউন্ড অ্যালার্ট চালু আছে', new_order: 'নতুন অর্ডার!', save: 'সেভ করুন', add_category: 'ক্যাটাগরি যোগ করুন', add_item: 'আইটেম যোগ করুন',
      edit: 'এডিট', delete: 'মুছুন', print: 'প্রিন্ট', add_tables: 'টেবিল যোগ করুন', menu_qr: 'মেনু QR (টেবিল ছাড়া)', open_menu: 'মেনু খুলুন',
      restaurants: 'রেস্টুরেন্ট', create_restaurant: 'রেস্টুরেন্ট তৈরি করুন', active: 'সক্রিয়', inactive: 'নিষ্ক্রিয়', activate: 'চালু করুন', deactivate: 'বন্ধ করুন',
      today_sales: 'আজকের বিক্রি (পরিবেশিত)', orders: 'অর্ডার', available: 'পাওয়া যাচ্ছে', unavailable: 'লুকানো', home_tag: 'রেস্টুরেন্টের জন্য QR মেনু ও অর্ডারিং',
      stats_rest: 'রেস্টুরেন্ট', stats_active: 'সক্রিয়', stats_orders: 'মোট অর্ডার', stats_today: 'আজকের অর্ডার'
    }
  };
  var lang = localStorage.getItem('om_lang') || 'en';
  var BN = '০১২৩৪৫৬৭৮৯';

  var OM = window.OM = {
    onLang: [],
    get lang() { return lang; },
    t: function (k) { return (I18N[lang] && I18N[lang][k]) || I18N.en[k] || k; },
    num: function (n) { var s = String(n); return lang === 'bn' ? s.replace(/\d/g, function (d) { return BN[d]; }) : s; },
    money: function (n) { return '৳' + OM.num(Math.round(parseFloat(n) * 100) / 100); },
    csrf: function () { var m = document.cookie.match(/csrftoken=([^;]+)/); return m ? m[1] : ''; },
    apply: function () {
      document.documentElement.lang = lang;
      document.querySelectorAll('[data-i18n]').forEach(function (e) { e.textContent = OM.t(e.dataset.i18n); });
      document.querySelectorAll('[data-i18n-ph]').forEach(function (e) { e.placeholder = OM.t(e.dataset.i18nPh); });
      document.querySelectorAll('[data-en]').forEach(function (e) { e.textContent = (lang === 'bn' && e.dataset.bn) ? e.dataset.bn : e.dataset.en; });
      document.querySelectorAll('[data-money]').forEach(function (e) { e.textContent = OM.money(e.dataset.money); });
      var lb = document.getElementById('langBtn'); if (lb) lb.textContent = lang === 'en' ? 'বাংলা' : 'English';
      OM.onLang.forEach(function (f) { f(); });
    }
  };

  function paintTheme() {
    var b = document.getElementById('themeBtn');
    if (b) b.textContent = document.documentElement.dataset.theme === 'dark' ? '☀️' : '🌙';
  }
  document.getElementById('langBtn').addEventListener('click', function () {
    lang = lang === 'en' ? 'bn' : 'en'; localStorage.setItem('om_lang', lang); OM.apply();
  });
  document.getElementById('themeBtn').addEventListener('click', function () {
    var t = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = t; localStorage.setItem('om_theme', t); paintTheme();
  });
  paintTheme(); OM.apply();
})();

# OrderMama – রেস্টুরেন্ট QR মেনু ও অর্ডার সিস্টেম

Stack: Django 5 + PostgreSQL + HTML/CSS/JS (কোনো ফ্রন্টএন্ড ফ্রেমওয়ার্ক নেই)

## তিনটি সেকশন
1. **কাস্টমার** `/r/<slug>/?table=5` – লগইন ছাড়া অর্ডার। নাম বাধ্যতামূলক, ফোন ঐচ্ছিক। অর্ডারের পর লাইভ স্ট্যাটাস পেজ।
2. **রেস্টুরেন্ট ড্যাশবোর্ড** `/dashboard/` – লাইভ অর্ডার (৫ সেকেন্ডে অটো রিফ্রেশ + সাউন্ড অ্যালার্ট), মেনু ম্যানেজ, টেবিল ও QR প্রিন্ট, ইতিহাস, সেটিংস।
3. **সুপার অ্যাডমিন** `/super/` – রেস্টুরেন্ট তৈরি (মালিকের ইউজারনেম/পাসওয়ার্ডসহ), চালু/বন্ধ, মোট পরিসংখ্যান।

সব পেজে ডার্ক/লাইট এবং বাংলা/English বাটন আছে।

## চালানোর ধাপ
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL ডাটাবেস বানাও
#   createdb ordermama      (অথবা pgAdmin থেকে)
# .env.example দেখে এনভায়রনমেন্ট ভেরিয়েবল সেট করো (DB_NAME, DB_USER, DB_PASSWORD ...)

python manage.py makemigrations qrmenu
python manage.py migrate
python manage.py createsuperuser        # এটাই সুপার অ্যাডমিন
python manage.py runserver
```
দ্রুত টেস্টের জন্য PostgreSQL ছাড়া: `USE_SQLITE=1 python manage.py runserver`

## ব্যবহার
1. `/login/` দিয়ে সুপার অ্যাডমিনে ঢোকো, **Create restaurant** দিয়ে রেস্টুরেন্ট ও মালিকের অ্যাকাউন্ট বানাও।
2. মালিক লগইন করে: Menu → ক্যাটাগরি ও আইটেম যোগ → Tables → টেবিল যোগ করে QR প্রিন্ট।
3. কাস্টমার QR স্ক্যান করলে ওই টেবিলের নম্বরসহ মেনু খোলে।

## প্রোডাকশনে
- `DEBUG=0`, শক্তিশালী `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SITE_URL=https://yourdomain.com` (QR কোডের লিংকের জন্য) সেট করো।
- `python manage.py collectstatic`; `media/` ফোল্ডার (লোগো ও ছবি) nginx দিয়ে সার্ভ করো।
- পেমেন্ট গেটওয়ে (bKash/Nagad) এখনো যোগ করা হয়নি।

# שיעור 8 — שיעורי בית: pipeline ל-ShopList

## מסמך דרישות

**המטרה:** לבנות pipeline ב-GitHub Actions, שבכל push בודק את ShopList, בונה את שלושת ה-images, ומעלה אותם ל-`ghcr.io`. ואז להתקין ב-cluster את מה שה-pipeline בנה.

**הגשה:** push מהבית, לפני שיעור 9.

**זמן משוער:** שעתיים וחצי. עשיתן קודם את [התרגולים](exercises.md)? פחות.

**איך לעבוד:** הדרישות מסודרות לפי הסדר. כל דרישה נשענת על הקודמת. בכל דרישה כתוב **איך בודקות שזה עובד**. לא עוברות לדרישה הבאה לפני שהבדיקה עברה.

---

## 0. הכנה (פעם אחת)

### מה צריך

- [ ] הריפו שלכן ב-GitHub, עם `app/` ו-`helm/shoplist/` משיעור 7
- [ ] **Actions מופעל:** בדף הריפו, לשונית Actions. יש כפתור ירוק "I understand my workflows"? ללחוץ
- [ ] Docker Desktop עם **Kubernetes running**, ו-Helm. רק לד6
- [ ] `kubectl config current-context` מחזיר `docker-desktop`

### להביא את הקוד

בתיקייה של הריפו שלכן: `git pull`.

### דחיפה (push) מהבית

כל הדרישות כאן נבדקות **ב-GitHub**, אחרי push. אז עושות push הרבה, וזה בסדר. רק מהבית, לא מהמחשב בכיתה.

---

## 1. התמונה הגדולה: מה יהיה בסוף

```
.github/
  workflows/
    ci.yml                 ← ד2–ד5
helm/
  shoplist/
    values-registry.yaml   ← ד6
lessons/08-cicd-pipeline/homework/
  answers.md
  screenshots/
    1-green.png
    2-red.png
    3-packages.png
    4-cluster.png
```

וב-GitHub: לשונית Actions עם ריצות ירוקות, ושלושה packages ב-`ghcr.io`.

---

## 2. הדרישות

### ד1 — Actions עובד

קובץ workflow קטן, `hello.yml`, לפי שלב 2 במדריך. push.

**בדיקה:** בלשונית Actions יש ריצה ירוקה של `Hello`. בצעד `What is in the repo?` רואים `app` ו-`helm`.

**אחרי שעבד:** למחוק את `hello.yml` (`git rm`), כדי שלא ירוץ בכל push.

### ד2 — job של בדיקות

קובץ `.github/workflows/ci.yml`, בשם `ShopList CI`, שרץ על push ל-`main`. job בשם `test`, עם הצעדים:

| צעד | מה הוא עושה |
|---|---|
| `Get the code` | `actions/checkout@v6` |
| `Backend - Python syntax check` | `python3 -m py_compile` על קובצי ה-Python ב-`app/backend` |
| `Stats - Node syntax check` | `node --check` על כל קובץ `.js` ב-`app/stats` |
| `Install Helm` | `azure/setup-helm@v5` |
| `Chart - helm lint` | `helm lint helm/shoplist` |

**בדיקה:** ריצה ירוקה. כל חמשת הצעדים עם ✓.

### ד3 — לשבור בכוונה

1. לשבור את ה-backend: נקודתיים חסרות בשורת `def`. push.
2. ריצה אדומה. הצעד `Backend - Python syntax check` אדום, והצעדים אחריו לא רצו.
3. לתקן, ו-push. ירוק שוב.

**צילום מסך 2:** הריצה האדומה, פתוחה על הצעד שנכשל, כך שרואים את השגיאה.

### ד4 — שלושה images ל-ghcr.io

להוסיף ל-`ci.yml`:

- `permissions` עם `contents: read` ו-`packages: write`
- job בשם `build`, שרץ **רק אחרי** ש-`test` הצליח
- `matrix` עם שלושת הסרוויסים: `backend`, `stats`, `frontend`
- שם ה-image: `ghcr.io/<owner באותיות קטנות>/shoplist-<service>`
- **שתי תגיות** לכל image: 7 התווים הראשונים של ה-commit, ו-`latest`
- login עם `secrets.GITHUB_TOKEN`. **בלי שום סיסמה בקובץ**

**בדיקה:**
- בדף הריצה: `test`, ואחריו שלושה `build` במקביל. הכל ירוק
- ב-Packages של הריפו: שלושה packages, לכל אחד תגית של 7 תווים ו-`latest`

**צילום מסך 1:** הגרף של הריצה הירוקה: test ושלושת ה-build.
**צילום מסך 3:** דף ה-Packages עם שלושת ה-images.

### ד5 — כפתור הרצה, ודף סיכום

1. להוסיף ל-`on:` את `workflow_dispatch`.
2. להוסיף ל-job `build` צעד אחרון, `Summary`, שכותב ל-`$GITHUB_STEP_SUMMARY` את שם ה-image והתגית.
3. בלשונית Actions, להריץ את ה-workflow מהכפתור **Run workflow**, בלי push.

**בדיקה:**
- בלשונית Actions, ליד הריצה החדשה כתוב `workflow_dispatch` ולא `push`
- בדף הסיכום של הריצה: שלוש שורות `Pushed ghcr.io/...:<תגית>`
- התגית זהה לתגית של הריצה הקודמת. למה? (זו שאלה 8 בד7)

### ד6 — מהמחסן אל ה-cluster

1. שלושת ה-packages: **Public**.
2. `helm/shoplist/values-registry.yaml`, לפי שלב 13 במדריך, עם השם שלכן במקום `OWNER`.
3. `helm upgrade --install shop` ב-namespace `shop`, עם `values-registry.yaml` ועם התגית מהריצה האחרונה, לשלושת הסרוויסים.

**בדיקה:**
- `kubectl get pods -n shop`: הכל `Running`
- ה-image של ה-backend הוא `ghcr.io/.../shoplist-backend:<התגית>` (הפקודה בשלב 14)
- `http://localhost:30080` עובד, והמוצרים שם

**צילום מסך 4:** הטרמינל עם הפלט של שתי הפקודות מהבדיקה, ומתחתיו `helm history shop -n shop`.

### ד7 — שאלות

ב-`lessons/08-cicd-pipeline/homework/answers.md`, תשובה של 2–4 משפטים לכל שאלה. במילים שלכן.

1. מה ההבדל בין CI, Continuous Delivery ו-Continuous Deployment? איפה ה-pipeline שלכן עומד?
2. ה-runner "ריק" בכל ריצה. תני שתי דוגמאות לדברים שזה מונע.
3. למה `build` צריך `needs: test`? מה היה קורה בלי זה, אם יש שגיאת תחביר ב-backend?
4. למה ב-`helm upgrade` השתמשת בתגית של ה-commit, ולא ב-`latest`? תני שתי סיבות.
5. ה-workflow שלך לא מכיל אף סיסמה. איך הוא בכל זאת מצליח להעלות ל-`ghcr.io`?
6. חברה רוצה להעלות images גם ל-Docker Hub. איפה היא שומרת את הסיסמה, ואיך ה-workflow מגיע אליה?
7. בלוג של ריצה אדומה כתוב `Process completed with exit code 1`. מה זה אומר, ואיך GitHub יודע להפסיק?
8. בד5 הרצת את ה-workflow מהכפתור, בלי commit חדש. למה התגית יצאה זהה לריצה הקודמת? האם זו בעיה?
9. מה עוד עשית ביד בד6, שלא היה צריך לעשות ביד? איך היית רוצה שזה יעבוד?

---

## 3. בונוסים

### בונוס ד8 — תג סטטוס ב-README

להוסיף ל-`README.md` בשורש הריפו תג (badge) שמראה אם ה-pipeline ירוק או אדום. רמז: בדף ה-workflow ב-Actions, בתפריט `...`, יש **Create status badge**.

### בונוס ד9 — לבנות רק מה שהשתנה

היום, שינוי ב-`README.md` מפעיל את כל ה-pipeline. להוסיף ל-`push` את `paths`, כך שה-pipeline ירוץ רק כששינו משהו ב-`app/`, ב-`helm/` או ב-`.github/workflows/`. לבדוק: שינוי ב-README לא מפעיל ריצה.

---

## 4. מה מגישות

- [ ] `.github/workflows/ci.yml` עובד, וההיסטוריה ב-Actions מראה ריצה אדומה וריצה ירוקה
- [ ] `helm/shoplist/values-registry.yaml`
- [ ] `answers.md` וארבעה צילומי מסך
- [ ] שלושה packages ציבוריים ב-`ghcr.io`
- [ ] push מהבית

---

## 5. ניקוד

| דרישה | נקודות |
|---|---|
| ד1: Actions עובד | 5 |
| ד2: job של בדיקות | 15 |
| ד3: לשבור ולתקן | 10 |
| ד4: matrix, ghcr.io, שתי תגיות | 25 |
| ד5: כפתור וסיכום | 10 |
| ד6: מהמחסן אל ה-cluster | 20 |
| ד7: שאלות | 15 |
| בונוס ד8, ד9 | +5 כל אחד |

---

## 6. תקלות שכדאי להכיר

| מה רואות | מה עושים |
|---|---|
| אין ריצות בלשונית Actions | Actions כבוי ב-fork. או נתיב לא נכון: `.github/workflows/`, עם נקודה |
| `Invalid workflow file` | YAML שבור. GitHub מראה שורה. רווחים, לא Tab |
| `helm lint` לא מוצא את ה-chart | `helm/shoplist` לא עלה לריפו. `git add helm/` |
| `repository name must be lowercase` | שם המשתמשת באותיות גדולות. `${GITHUB_REPOSITORY_OWNER,,}` |
| `denied: permission_denied: write_package` | חסר `packages: write` ב-`permissions` |
| `denied: ... installation not allowed to Write organization package` | יש כבר package באותו שם, שלא נוצר מהריפו הזה. Package settings ← Manage Actions access ← להוסיף את הריפו, עם Write |
| `invalid reference format` | התגית או השם ריקים. המשתנים נשמרו ל-`$GITHUB_ENV`? |
| `ErrImagePull` ב-cluster | ה-package פרטי, או תגית שגויה. להעתיק מה-Summary |

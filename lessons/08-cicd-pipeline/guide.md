# שיעור 8 — CI/CD: הרובוט שבונה בשבילנו
## מדריך לסטודנטית

---

## מה יהיה בסוף השיעור

- בריפו שלכן ב-GitHub, קובץ אחד: `.github/workflows/ci.yml`
- בכל `git push`, GitHub מריץ לבד בדיקות, בונה את שלושת ה-images, ושולח אותם ל-`ghcr.io`
- בדף הריפו, בלשונית **Packages**: שלושה images, כל אחד עם תגית של ה-commit שבנה אותו
- האפליקציה ShopList רצה ב-cluster שלכן, מ-images שה-pipeline בנה, ולא מ-images שבניתן ביד

**מה תדעו לעשות:**
- להסביר מה זה CI, מה זה CD, ומה זה pipeline
- לקרוא ולכתוב workflow של GitHub Actions: `on`, `jobs`, `steps`, `runs-on`, `uses`, `run`
- לגרום ל-pipeline לעצור כשבדיקה נכשלת, ולקרוא את הלוג כדי להבין למה
- להסביר מה זה registry, ולמה התגית של ה-commit עדיפה על `latest`
- לבנות שלושה images ב-job אחד, עם `matrix`
- למשוך image מ-`ghcr.io` ולהתקין אותו ב-cluster עם Helm

**איך השיעור עובד:** בשיעור אני מדגימה על הריפו שלי, ואתן עוקבות במדריך הזה. את הכל מתרגלות בבית, ב-[exercises.md](exercises.md). התרגולים לא מוגשים, אבל מכינים לשיעורי הבית.

**עוד לא:** את ה-`helm upgrade` בסוף עדיין מריצות ביד. בשיעור 9 גם הצעד הזה יקרה לבד, עם Argo CD.

---

## לפני שמתחילות (בבית)

- [ ] יש לכן חשבון GitHub, והריפו `devops-2027-shoplist` שלכן נמצא שם (fork, כמו בשיעורים הקודמים)
- [ ] בריפו יש את `helm/shoplist/` משיעור 7. ה-pipeline בודק אותו
- [ ] בריפו יש את `app/backend`, `app/stats` ו-`app/frontend`, כל אחד עם `Dockerfile` משיעורי הבית של שיעור 4. ה-pipeline בונה מהם
- [ ] **Actions מופעל ב-fork.** ב-fork חדש, GitHub מכבה את Actions. בדף הריפו: לשונית **Actions**. רואות כפתור ירוק **I understand my workflows, go ahead and enable them**? ללחוץ עליו, פעם אחת
- [ ] Docker Desktop עם **Kubernetes running**, ו-Helm. צריך רק לחלק 7

> **מאיפה עושות push?** רק מהבית. לא מהמחשב בכיתה.

---

## חלק 1 — למה CI/CD?

### הבעיה: כל שינוי, אותם שבעה צעדים ביד

נניח ששיניתן שורה אחת ב-backend. כדי שהשינוי יגיע ל-cluster, מה עשיתן עד היום?

1. לבדוק שהקוד בכלל עובד
2. `docker build` ל-backend
3. לבחור תגית, ולזכור אותה
4. לבנות גם את stats ואת frontend, אם גם הם השתנו
5. להעלות את ה-images למקום שה-cluster יכול להגיע אליו
6. `helm upgrade` עם התגית החדשה
7. לבדוק שהכל עלה

שבעה צעדים, ביד, בכל שינוי. ומה יכול להשתבש?

- שכחתן את צעד 1, ושלחתן קוד שבור
- בניתן מהמחשב שלכן, עם קובץ שלא עשיתן לו commit. אף אחד אחר לא יכול לבנות אותו image שוב
- שתי בנות בצוות בנו באותו יום, עם אותה תגית
- "אצלי זה עובד": המחשב שלכן שונה מהמחשב של חברה

### הפתרון: רובוט שעושה את הצעדים, בכל push

**המשפט של היום:** **"כל push עובר את אותה דרך, בלי ידיים."**

אנחנו כותבות פעם אחת, בקובץ, את הצעדים. ומאז, בכל `git push`, מחשב נקי ב-GitHub מריץ אותם לפי הסדר. אם צעד נכשל, הוא עוצר, ומודיע.

---

## חלק 2 — מושגים חדשים

### המושגים CI, CD ו-pipeline

| מושג | ראשי תיבות | מה זה אומר |
|---|---|---|
| **CI** | Continuous Integration | כל push נבדק ונבנה מיד, אוטומטית. מגלים תקלה אחרי דקות, לא אחרי שבוע |
| **CD** | Continuous Delivery | כל push שעבר את הבדיקות מוכן להתקנה: יש image ב-registry, עם תגית |
| **CD** | Continuous Deployment | עוד צעד: גם ההתקנה עצמה קורית לבד. זה שיעור 9 |
| **pipeline** | — | רשימת הצעדים, לפי הסדר: בדיקה, בנייה, העלאה, התקנה |

**היום:** CI, וחצי מ-CD. ה-pipeline בודק, בונה ומעלה. את ההתקנה עוד מריצות ביד.

### האנלוגיה: הקונדיטוריה, ובקרת האיכות

ממשיכות עם רשת הקונדיטוריות משיעור 5. עד היום, אתן אפיתן כל עוגה בעצמכן, במטבח שלכן בבית, והבאתן אותה לסניף. מהיום יש **מטבח מרכזי**:

| בקונדיטוריה | ב-CI/CD |
|---|---|
| המתכון הכתוב, שכל עובדת יכולה לבצע | ה-workflow: הקובץ `ci.yml` |
| הפעמון: "הזמנה חדשה נכנסה" | ה-event: `push` |
| מטבח שכור לשעה. מגיעים, הוא נקי. יוצאים, מנקים אותו | ה-runner: מחשב נקי של GitHub, לכל ריצה |
| תחנה במטבח: תחנת טעימות, תחנת אפייה | job |
| שורה במתכון: "לערבב", "לאפות 20 דקות" | step |
| כלי מוכן מהחנות: מיקסר | action (`uses:`) |
| פעולה שעושים בידיים | פקודה (`run:`) |
| בקרת איכות: טועמים לפני שאורזים | job של בדיקות |
| המחסן המרכזי, עם קופסאות מתויגות | ה-registry: `ghcr.io` |
| מספר אצווה על הקופסה: 7f3a2c1 | תגית לפי ה-commit |
| מדבקה "הכי טרי", שעוברת כל בוקר לקופסה אחרת | התגית `latest` |

**הרעיון החשוב:** המטבח השכור **ריק** בכל פעם. אין בו את הקוד שלכן, אין בו את מה שבניתן אתמול. כל מה שצריך, המתכון מביא בעצמו. לכן "אצלי זה עובד" כבר לא קיים: יש רק "במטבח הנקי זה עובד", או לא.

### מילון קצר של GitHub Actions

השירות **GitHub Actions** הוא שירות ה-CI/CD שבנוי בתוך GitHub. אין מה להתקין. מספיק לשים קובץ YAML בתיקייה הנכונה.

| מילה | מה זה | דוגמה |
|---|---|---|
| **workflow** | קובץ YAML אחד ב-`.github/workflows/`. מתכון שלם | `ci.yml` |
| **event** | מה מפעיל את ה-workflow | `push`, `pull_request`, לחיצה על כפתור |
| **job** | קבוצת צעדים שרצה על runner אחד | `test`, `build` |
| **step** | צעד אחד. פקודה, או action | `docker build ...` |
| **runner** | המחשב שמריץ job. של GitHub, נקי, ונמחק בסוף | `ubuntu-latest` |
| **action** | צעד מוכן, שמישהו כתב ופרסם | `actions/checkout@v6` |

> **כל ה-jobs רצים במקביל.** אם לא אמרנו אחרת, כל ה-jobs ב-workflow מתחילים יחד, כל אחד במטבח משלו. רוצות סדר? `needs:`. נראה בחלק 4.

---

## חלק 3 — ה-workflow הראשון

### שלב 1 — איפה הקובץ גר

השירות GitHub מחפש workflows בתיקייה אחת בלבד, בשורש הריפו:

```
devops-2027-shoplist/
  .github/
    workflows/
      hello.yml       ← כל קובץ כאן הוא workflow
  app/
  helm/
```

**שימו לב לנקודה:** `.github`, עם נקודה בהתחלה. בלי הנקודה, GitHub לא יראה את הקובץ, ולא תהיה שום שגיאה. פשוט שום דבר לא ירוץ.

### שלב 2 — hello.yml

```yaml
# .github/workflows/hello.yml - the first workflow
# Runs on every push. Prints a greeting and shows what the runner has.

name: Hello

on: push

jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - name: Say hello
        run: echo "Hello from the robot kitchen"

      - name: Who am I, and where?
        run: |
          echo "Repo:   $GITHUB_REPOSITORY"
          echo "Commit: $GITHUB_SHA"
          uname -a
          docker --version
          python3 --version
          node --version

      - name: Get the code
        uses: actions/checkout@v6

      - name: What is in the repo?
        run: ls
```

**שורה אחר שורה:**

| שורה | מה היא אומרת |
|---|---|
| `name: Hello` | השם שיופיע בלשונית Actions |
| `on: push` | מתי לרוץ: בכל push, לכל branch |
| `jobs:` | מכאן, רשימת ה-jobs |
| `hello:` | שם ה-job. אנחנו בוחרות אותו |
| `runs-on: ubuntu-latest` | על איזה מחשב: Linux נקי של GitHub |
| `steps:` | רשימת הצעדים, לפי הסדר. כל צעד מתחיל ב-`-` |
| `name:` בתוך צעד | מה יופיע בלוג. לא חובה, אבל עוזר מאוד |
| `run:` | פקודת shell, כמו בטרמינל |
| `run: \|` | כמה פקודות, שורה אחרי שורה. ה-`\|` אומר "הטקסט ממשיך בשורות הבאות" |
| `uses:` | צעד מוכן. כאן: להביא את הקוד מהריפו אל ה-runner |

### שלב 3 — `uses` מול `run`

| | `run:` | `uses:` |
|---|---|---|
| מה זה | פקודה שאתן כותבות | צעד מוכן, שמישהו כתב |
| דומה ל | לערבב ביד | מיקסר מהחנות |
| דוגמה | `run: docker build ...` | `uses: actions/checkout@v6` |
| מאיפה | מהראש שלכן | מ-GitHub: `בעלים/שם@גרסה` |

**למה `actions/checkout`?** זוכרות שהמטבח ריק? ה-runner מתחיל בלי הקוד שלכן. הצעד הזה עושה `git clone` לריפו, ל-commit שהפעיל את הריצה. בלעדיו, `ls` מחזיר תיקייה ריקה.

**מה זה `@v6`?** הגרסה של ה-action. תמיד לכתוב גרסה, כמו שלא כותבים `FROM python` בלי גרסה.

### שלב 4 — push, ולראות אותו רץ

```shell
git add .github/workflows/hello.yml
git commit -m "First workflow"
git push
```

ואז, בדף הריפו ב-GitHub:

1. לשונית **Actions**
2. בראש הרשימה: ריצה עם הודעת ה-commit, `First workflow`. ליד: עיגול צהוב שמסתובב, ואחר כך ✓ ירוק
3. ללחוץ על הריצה, ואז על ה-job `hello`
4. כל צעד אפשר לפתוח, ולראות בדיוק מה הוא הדפיס

**מה רואים בצעד "Who am I"?** את ה-commit, גרסת Docker, Python ו-Node. כל אלה כבר מותקנים על ה-runner. לא היינו צריכות להתקין כלום.

**מה רואים בצעד "What is in the repo"?** את התיקיות `app` ו-`helm`. ה-checkout הביא אותן.

> **ניסוי קטן:** להזיז את הצעד `Get the code` להיות הצעד האחרון, ולעשות push. מה `ls` מראה עכשיו? (תרגול 2 ב-exercises)

---

## חלק 4 — בקרת איכות: job של בדיקות

### מה אפשר לבדוק ב-ShopList?

עוד אין לנו בדיקות אמיתיות לקוד. אבל יש שלוש בדיקות פשוטות, שתופסות טעויות אמיתיות:

| בדיקה | פקודה | מה היא תופסת |
|---|---|---|
| Python מתקמפל? | `python3 -m py_compile app/backend/*.py` | שגיאת תחביר ב-backend: נקודתיים חסרות, סוגריים, הזחה |
| JavaScript תקין? | `node --check app/stats/server.js` | שגיאת תחביר ב-stats |
| ה-chart תקין? | `helm lint helm/shoplist` | YAML שבור, או חור עם שם שגוי |

**למה זה שווה משהו?** שגיאת תחביר ב-backend תגרום ל-pod לקרוס ב-`CrashLoopBackOff`. עדיף לגלות את זה אחרי דקה ב-GitHub, מאשר אחרי חצי שעה ב-cluster.

> **בעולם האמיתי:** כאן רצות גם בדיקות יחידה (`pytest`, `npm test`), בדיקות סגנון (linters), וסריקת אבטחה ל-image. הרעיון זהה: כל בדיקה היא צעד, וצעד שנכשל עוצר הכל.

### שלב 5 — ci.yml, עם job אחד: test

עכשיו הקובץ האמיתי. אפשר למחוק את `hello.yml`, הוא עשה את שלו.

```yaml
# .github/workflows/ci.yml - stage 1: test only

name: ShopList CI

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Get the code
        uses: actions/checkout@v6

      - name: Backend - Python syntax check
        run: python3 -m py_compile app/backend/*.py

      - name: Stats - Node syntax check
        run: for f in app/stats/*.js; do node --check "$f"; done

      - name: Install Helm
        uses: azure/setup-helm@v5

      - name: Chart - helm lint
        run: helm lint helm/shoplist
```

**מה חדש:**

- `branches: [main]`: לרוץ רק על push ל-`main`. לא על כל branch
- `azure/setup-helm@v5`: action שמתקין Helm על ה-runner. עוד מיקסר מהחנות
- `for f in ...; do ...; done`: לולאה. `node --check` בודק קובץ אחד בכל פעם, אז עוברות על כל קובצי ה-`.js`, אחד אחרי השני

### שלב 6 — לשבור בכוונה

הדרך היחידה לדעת שבקרת האיכות עובדת: להגיש לה עוגה שרופה.

ב-`app/backend/app.py`, למחוק את הנקודתיים בסוף שורה של `def`. למשל:

```python
def health()
```

ואז:

```shell
git commit -am "Break the backend on purpose"
git push
```

**מה רואים ב-Actions:**

- ✗ אדום ליד הריצה
- בתוך ה-job: הצעד `Backend - Python syntax check` אדום. הצעדים אחריו **לא רצו בכלל**
- בלוג של הצעד:

```
  File "app/backend/app.py", line 32
    def health()
                ^
SyntaxError: expected ':'
Error: Process completed with exit code 1.
```

**איך GitHub יודע שהצעד נכשל?** כל פקודה מחזירה מספר כשהיא מסיימת: `0` = הצלחה, כל דבר אחר = כישלון. `py_compile` מצא שגיאה, החזיר `1`, ו-GitHub עצר.

**ועוד:** GitHub שולח מייל לבעלת הריפו: "Run failed". אף אחד לא צריך לזכור לבדוק.

לתקן, ולעשות push שוב. ✓ ירוק.

---

## חלק 5 — המחסן: registry

### למה צריך registry?

ה-runner בנה image. ואז? בסוף הריצה **המטבח נמחק**, ויחד איתו ה-image. צריך לשלוח אותו למקום קבוע, שגם ה-cluster יכול להגיע אליו.

ה-**registry** הוא מחסן של images. כבר השתמשתן באחד: **Docker Hub**. משם הגיע `postgres:15-alpine`.

היום נשתמש ב-**GitHub Container Registry**, בכתובת `ghcr.io`. למה?

- הוא כבר מחובר לחשבון GitHub שלכן. אין עוד חשבון לפתוח
- ה-workflow מקבל אליו הרשאה אוטומטית. אין סיסמה לשמור

### שם של image ב-registry

```
ghcr.io / rivkak / shoplist-backend : 7f3a2c1
   ↑         ↑           ↑               ↑
 המחסן   הבעלים    שם הקופסה      התגית
```

| חלק | מה זה | מאיפה |
|---|---|---|
| `ghcr.io` | כתובת ה-registry | קבוע |
| `rivkak` | שם המשתמשת ב-GitHub, **באותיות קטנות** | `github.repository_owner` |
| `shoplist-backend` | שם ה-image | אנחנו בוחרות |
| `7f3a2c1` | התגית | 7 התווים הראשונים של ה-commit |

> **אותיות קטנות!** registry לא מקבל אותיות גדולות בשם. אם שם המשתמשת שלכן הוא `RivkaK`, ה-push ייכשל עם `repository name must be lowercase`. ב-workflow נמיר לאותיות קטנות.

### תגית: מספר אצווה, או מדבקה שזזה?

| | התגית של ה-commit: `7f3a2c1` | `latest` |
|---|---|---|
| בקונדיטוריה | מספר אצווה מודפס על הקופסה | מדבקה "הכי טרי", שמחר תעבור לקופסה אחרת |
| משתנה? | לעולם לא. אותו commit, אותו image | כל push מזיז אותה |
| יודעות מה רץ? | כן: `git show 7f3a2c1` מראה בדיוק איזה קוד | לא. "latest של מתי?" |
| rollback | `--set backend.image.tag=` לתגית הקודמת | אי אפשר. הקודם כבר לא `latest` |

**הכלל:** ב-cluster, תמיד תגית של commit. `latest` רק לנוחות, כשמנסות משהו ביד.

### ההרשאה: GITHUB_TOKEN

כדי להעלות למחסן, צריך מפתח. בכל ריצה, GitHub מייצר מפתח זמני: `secrets.GITHUB_TOKEN`. הוא תקף רק לריצה הזו, ורק לריפו הזה.

אבל כברירת מחדל, המפתח הזה יכול רק **לקרוא**. כדי לכתוב ל-registry, מבקשות במפורש:

```yaml
permissions:
  contents: read      # read the code
  packages: write     # push images to ghcr.io
```

**למה לא לתת הכל תמיד?** אותו עיקרון כמו מפתח לעובדת חדשה: רק לחדרים שהיא צריכה. אם מישהו גונב את המפתח באמצע ריצה, הוא יכול לעשות רק את מה שהמפתח מרשה.

### שלב 7 — job שני: build-backend

מוסיפות ל-`ci.yml`. את ה-`permissions` שמים מעל `jobs:`, ואת ה-job החדש מתחת ל-`test`:

```yaml
permissions:
  contents: read      # read the code
  packages: write     # push images to ghcr.io

jobs:
  test:
    # ... exactly as before ...

  build-backend:
    needs: test                 # only after test passed
    runs-on: ubuntu-latest
    steps:
      - name: Get the code
        uses: actions/checkout@v6

      - name: Image name and tag
        run: |
          # registry names must be lowercase
          echo "OWNER=${GITHUB_REPOSITORY_OWNER,,}" >> "$GITHUB_ENV"
          # short commit id, like a batch number: a1b2c3d
          echo "TAG=${GITHUB_SHA::7}" >> "$GITHUB_ENV"

      - name: Log in to ghcr.io
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" |
            docker login ghcr.io -u "${{ github.actor }}" --password-stdin

      - name: Build
        run: docker build -t "ghcr.io/$OWNER/shoplist-backend:$TAG" app/backend

      - name: Push
        run: docker push "ghcr.io/$OWNER/shoplist-backend:$TAG"
```

**מה חדש:**

| שורה | מה היא עושה |
|---|---|
| `needs: test` | לחכות ש-`test` יסתיים בהצלחה. נכשל? ה-job הזה לא ירוץ בכלל |
| `${GITHUB_REPOSITORY_OWNER,,}` | שם הבעלים. ה-`,,` בסוף ממיר לאותיות קטנות (bash) |
| `${GITHUB_SHA::7}` | ה-commit המלא הוא 40 תווים. `::7` לוקח את 7 הראשונים |
| `>> "$GITHUB_ENV"` | לשמור משתנה, כך שגם הצעדים הבאים יראו אותו. בלי זה, המשתנה נעלם בסוף הצעד |
| `${{ secrets.GITHUB_TOKEN }}` | המפתח הזמני. GitHub מכניס אותו לפני שהפקודה רצה |
| `${{ github.actor }}` | מי עשתה את ה-push |
| `docker login`, `build`, `push` | את `docker build` כבר הקלדתן ביד בשיעורים 3–4. `docker login` (להיכנס למחסן) ו-`docker push` (להעלות אליו) חדשות. ועכשיו את שלושתן מקליד הרובוט |

### שתי צורות של משתנים

| צורה | מי מחליף אותה | מתי |
|---|---|---|
| `${{ ... }}` | GitHub | לפני שהצעד מתחיל. GitHub כותב את הערך לתוך הפקודה |
| `$OWNER`, `$GITHUB_SHA` | ה-shell של ה-runner | בזמן שהפקודה רצה |

**כלל אצבע:** `secrets`, `matrix` ו-`github.actor`: עם `${{ }}`. משתני סביבה: עם `$`.

### שלב 8 — לראות את ה-image במחסן

אחרי ה-push וה-✓ הירוק:

1. בדף הריפו, בצד ימין: **Packages**. (או בפרופיל שלכן, לשונית Packages)
2. רואות `shoplist-backend`
3. בפנים: התגית, למשל `7f3a2c1`, ופקודת `docker pull` מוכנה להעתקה

---

## חלק 6 — שלושה סרוויסים: matrix

### הבעיה: שלוש פעמים אותו job

צריך לבנות גם את stats ואת frontend. אפשר להעתיק את `build-backend` עוד פעמיים. אבל שלושה העתקים = שלושה מקומות לתקן. זוכרות את שיעור 7? בדיוק בשביל זה המצאנו חורים.

### מטריצה (matrix): אותו מתכון, שלושה מטבחים

```yaml
  build:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [backend, stats, frontend]
```

השירות GitHub יוצר **שלושה עותקים** של ה-job. בכל עותק, `${{ matrix.service }}` מקבל ערך אחר. ושלושתם רצים **במקביל**, כל אחד במטבח משלו.

| עותק | `matrix.service` | בונה מתוך | image |
|---|---|---|---|
| 1 | `backend` | `app/backend` | `shoplist-backend` |
| 2 | `stats` | `app/stats` | `shoplist-stats` |
| 3 | `frontend` | `app/frontend` | `shoplist-frontend` |

**זה עובד רק כי** בחרנו שמות עקביים: התיקייה, ה-image, והמגירה ב-values. סדר משתלם.

### שלב 9 — ci.yml המלא

```yaml
# .github/workflows/ci.yml - ShopList CI
#
# On every push to main:
#   1. test   - syntax checks and helm lint
#   2. build  - three images in parallel (matrix), pushed to ghcr.io
#               with two tags: the short commit id, and latest
# Run by hand: Actions tab -> ShopList CI -> Run workflow

name: ShopList CI

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read      # read the code
  packages: write     # push images to ghcr.io

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Get the code
        uses: actions/checkout@v6

      - name: Backend - Python syntax check
        run: python3 -m py_compile app/backend/*.py

      - name: Stats - Node syntax check
        run: for f in app/stats/*.js; do node --check "$f"; done

      - name: Install Helm
        uses: azure/setup-helm@v5

      - name: Chart - helm lint
        run: helm lint helm/shoplist

  build:
    needs: test                                 # only after test passed
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [backend, stats, frontend]     # three copies of this job, in parallel
    steps:
      - name: Get the code
        uses: actions/checkout@v6

      - name: Image name and tag
        run: |
          # registry names must be lowercase
          echo "OWNER=${GITHUB_REPOSITORY_OWNER,,}" >> "$GITHUB_ENV"
          # short commit id, like a batch number: a1b2c3d
          echo "TAG=${GITHUB_SHA::7}" >> "$GITHUB_ENV"

      - name: Log in to ghcr.io
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" |
            docker login ghcr.io -u "${{ github.actor }}" --password-stdin

      - name: Build
        run: |
          IMAGE="ghcr.io/$OWNER/shoplist-${{ matrix.service }}"
          docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" \
            "app/${{ matrix.service }}"

      - name: Push
        run: |
          IMAGE="ghcr.io/$OWNER/shoplist-${{ matrix.service }}"
          docker push "$IMAGE:$TAG"
          docker push "$IMAGE:latest"

      - name: Summary
        run: echo "Pushed ghcr.io/$OWNER/shoplist-${{ matrix.service }}:$TAG" >> "$GITHUB_STEP_SUMMARY"
```

**מה עוד חדש:**

| שורה | מה היא עושה |
|---|---|
| `workflow_dispatch:` | כפתור **Run workflow** בלשונית Actions. להריץ ביד, בלי push |
| `-t ... -t ...` | שתי תגיות לאותו image: ה-commit, ו-`latest` |
| `$GITHUB_STEP_SUMMARY` | מה שכותבים לשם, מופיע בדף הסיכום של הריצה |

### שלב 10 — לקרוא את הגרף

אחרי push, בדף הריצה, GitHub מצייר את ה-pipeline:

```
          ┌── build (backend)  ──┐
 test ────┼── build (stats)    ──┼──  ✓
          └── build (frontend) ──┘
```

- `test` קודם, לבד
- אחריו שלושה `build` **יחד**. ככה שלושה images נבנים בזמן של אחד

**ומה אם test נכשל?** שלושת ה-build מסומנים באפור: **skipped**. אף image לא עלה למחסן. בדיוק מה שרצינו: עוגה שלא עברה טעימה, לא נארזת.

---

## חלק 7 — מהמחסן אל ה-cluster

ה-pipeline העלה images. עכשיו ה-cluster צריך למשוך אותם.

### שלב 11 — לפתוח את המחסן לקריאה

כל package חדש ב-`ghcr.io` נוצר **פרטי**. ה-cluster לא יודע את הסיסמה שלכן, אז הוא לא יכול למשוך.

הכי פשוט: להפוך את שלושת ה-packages לציבוריים. הקוד ממילא ציבורי.

לכל אחד משלושת ה-packages:

1. בדף ה-package: **Package settings** (למטה בצד)
2. למטה, ב-**Danger Zone**: **Change visibility** ← **Public**
3. להקליד את שם ה-package, ולאשר

> **בעבודה:** ה-images פרטיים, וה-cluster מקבל מפתח קריאה בתוך Secret מסוג `docker-registry` (`imagePullSecrets`). אותו רעיון כמו ה-Secret של postgres.

### שלב 12 — לבדוק שאפשר למשוך

```shell
docker pull ghcr.io/<המשתמשת שלכן>/shoplist-backend:<התגית>
```

**צפוי:** `Status: Downloaded newer image`. בלי `docker login`. אם מקבלות `denied` או `unauthorized`: ה-package עדיין פרטי.

### שלב 13 — values-registry.yaml

בשיעור 7 ה-chart משך images מקומיים: `imagePullPolicy: Never`, תגית `local`. עכשיו צריך טופס אחר, שמצביע על המחסן. קובץ חדש, `helm/shoplist/values-registry.yaml`:

```yaml
# values-registry.yaml - images from GitHub Container Registry (built by the CI pipeline)
# Replace OWNER with your GitHub user name, in lowercase.

imagePullPolicy: IfNotPresent   # a commit id never changes, so a local copy is safe

backend:
  image:
    repository: ghcr.io/OWNER/shoplist-backend
    tag: latest                 # only a fallback. Pass the commit id with --set

stats:
  image:
    repository: ghcr.io/OWNER/shoplist-stats
    tag: latest

frontend:
  image:
    repository: ghcr.io/OWNER/shoplist-frontend
    tag: latest
```

**למה `IfNotPresent`?** תגית של commit לא משתנה לעולם. אם ה-node כבר הוריד אותה, אין סיבה להוריד שוב.

### שלב 14 — helm upgrade, עם התגית מה-pipeline

את התגית לוקחות מה-Summary של הריצה האחרונה ב-Actions:

```shell
TAG=7f3a2c1
helm upgrade --install shop ./helm/shoplist -n shop --create-namespace \
  -f helm/shoplist/values-registry.yaml \
  --set backend.image.tag=$TAG \
  --set stats.image.tag=$TAG \
  --set frontend.image.tag=$TAG
```

**בדיקה:**

```shell
kubectl get pods -n shop
kubectl get deploy backend -n shop -o jsonpath='{.spec.template.spec.containers[0].image}'
```

**צפוי:** כל ה-pods `Running`, וה-image הוא `ghcr.io/.../shoplist-backend:7f3a2c1`. וב-`localhost:30080`, ShopList עובדת.

**מה השתנה כאן?** אף אחת לא הריצה `docker build` על המחשב שלה. ה-image נבנה במטבח הנקי, מקוד שנמצא ב-GitHub, עם מספר אצווה שאפשר לעקוב אחריו. כל אחת בצוות יכולה להתקין בדיוק את אותו דבר.

### מה עוד ביד?

רק הצעד האחרון: להעתיק תגית, ולהריץ `helm upgrade`. בשיעור 9 נעביר גם אותו לרובוט, עם **Argo CD**: כלי שיושב בתוך ה-cluster, מסתכל על הריפו, ומתקין לבד כל שינוי.

---

## חלק 8 — סודות

### המפתח GITHUB_TOKEN לא מספיק לכל דבר

המפתח `GITHUB_TOKEN` פותח רק את GitHub עצמו. מה אם ה-pipeline צריך להעלות ל-Docker Hub, או להתחבר לענן? צריך סיסמה של מישהו אחר.

**לעולם לא בקובץ.** ה-workflow נמצא בריפו, וכל מי שרואה את הריפו רואה אותו.

### איפה כן: Secrets של הריפו

1. בדף הריפו: **Settings** ← **Secrets and variables** ← **Actions**
2. **New repository secret**: שם, למשל `DOCKERHUB_TOKEN`, והערך
3. ב-workflow: `${{ secrets.DOCKERHUB_TOKEN }}`

**מה GitHub עושה עם זה:**

- את הערך אי אפשר לקרוא שוב, אפילו לא אתן. רק להחליף
- אם הערך מודפס בלוג, GitHub מסתיר אותו ומציג `***`
- ב-Pull Request שמגיע מ-fork של מישהי אחרת, הסודות **לא** נשלחים. אחרת כל אחד יכול היה לכתוב workflow שגונב אותם

> **זוכרות את המעטפה משיעור 6?** Secret ב-Kubernetes הוא מעטפה בתוך ה-cluster. Secret ב-GitHub הוא מעטפה בתוך GitHub. אותו רעיון: הסיסמה לא כתובה בקוד.

---

## חלק 9 — מילון

| מילה או פקודה | מה זה |
|---|---|
| `.github/workflows/` | התיקייה היחידה שבה GitHub מחפש workflows |
| `on: push` | לרוץ בכל push |
| `on: workflow_dispatch` | כפתור "Run workflow" |
| `runs-on: ubuntu-latest` | ה-runner: Linux נקי של GitHub |
| `steps:` | רשימת צעדים, לפי הסדר |
| `run:` | פקודת shell |
| `uses: owner/name@v1` | action מוכן |
| `needs: test` | לחכות ל-job אחר, ולרוץ רק אם הצליח |
| `strategy.matrix` | אותו job, כמה עותקים, במקביל |
| `permissions:` | מה מותר ל-`GITHUB_TOKEN` |
| `${{ secrets.X }}` | סוד מ-Settings, או `GITHUB_TOKEN` |
| `${{ github.sha }}`, `$GITHUB_SHA` | ה-commit שהפעיל את הריצה |
| `$GITHUB_ENV` | לשמור משתנה לצעדים הבאים |
| `$GITHUB_STEP_SUMMARY` | לכתוב לדף הסיכום |
| `ghcr.io` | ה-registry של GitHub |
| exit code `0` | הצלחה. כל מספר אחר: כישלון, וה-job נעצר |

---

## חלק 10 — ובעולם האמיתי?

### עוד כלים, אותו רעיון

| כלי | איפה גר | הקובץ |
|---|---|---|
| **GitHub Actions** | בתוך GitHub | `.github/workflows/*.yml` |
| **GitLab CI** | בתוך GitLab | `.gitlab-ci.yml`. נראה בשיעור 9 |
| **Jenkins** | שרת שמתקינים לבד | `Jenkinsfile` |
| **CircleCI**, **Azure Pipelines** | שירותים בענן | קובץ YAML בריפו |

כולם עושים אותו דבר: event, runner, jobs, steps. מי שמבינה אחד, קוראת את כולם.

### מה מוסיפים ב-pipeline של חברה

- **בדיקות אמיתיות:** `pytest`, `npm test`, בדיקות שמריצות את האפליקציה עם מסד נתונים
- **actions מוכנים ל-Docker:** `docker/build-push-action` במקום `docker build` ו-`push` ביד. עם cache, כך שבנייה חוזרת לוקחת שניות
- **סריקת אבטחה:** כלי כמו Trivy סורק את ה-image ומחפש חולשות ידועות, לפני ה-push
- **בדיקה לפני המיזוג:** בחברה לא עושים push ישר ל-`main`. עובדים על branch, ופותחים Pull Request. עם `on: pull_request`, ה-pipeline בודק את השינוי **לפני** שהוא נכנס. ו-`if:` על ה-job של ה-build, כך שעל PR רק בודקים, ולא מעלים images
- **הגנה על main:** ב-Settings ← Branches: אי אפשר למזג PR ל-`main` אם ה-pipeline אדום
- **סביבות:** קודם `staging`, ורק אחרי אישור של אדם, `production`

### מטבח משלכן: runners של החברה

ה-runners של GitHub חינמיים לריפו ציבורי. חברות שצריכות מחשב חזק, או גישה לרשת פנימית, מתקינות **self-hosted runner**: מחשב משלהן שמקבל עבודה מ-GitHub. כמו מטבח שבבעלותכן, במקום מטבח שכור.

---

## תקלות נפוצות

| מה רואות | למה | מה עושים |
|---|---|---|
| אין שום ריצה בלשונית Actions | Actions כבוי ב-fork, או שהקובץ לא ב-`.github/workflows/` | לשונית Actions ← enable. לבדוק את הנתיב, כולל הנקודה ב-`.github` |
| `Invalid workflow file` | שגיאת YAML: הזחה, או `-` חסר | GitHub מראה את מספר השורה. רווחים, לא Tab |
| `py_compile`: `SyntaxError` | שגיאת תחביר ב-backend | לפתוח את הלוג, לראות שורה, לתקן |
| `helm lint`: `Error: ... not found` | `helm/shoplist` לא בריפו, או בשם אחר | `git add helm/` ו-push. לבדוק את הנתיב |
| `repository name must be lowercase` | אותיות גדולות בשם המשתמשת | `${GITHUB_REPOSITORY_OWNER,,}` |
| `denied: permission_denied: write_package` | אין `packages: write` | להוסיף `permissions:` מעל `jobs:` |
| `unauthorized` ב-`docker login` | `secrets.GITHUB_TOKEN` כתוב לא נכון | בדיוק כך: `${{ secrets.GITHUB_TOKEN }}` |
| `build` מסומן **skipped** | `test` נכשל | לתקן את מה ש-`test` מצא, ו-push |
| `ErrImagePull` ב-cluster | ה-package פרטי, או תגית שלא קיימת | Package settings ← Public. להעתיק את התגית מה-Summary |
| ה-cluster מריץ קוד ישן | התגית `latest` עם `IfNotPresent` | תמיד תגית של commit |
| `$TAG` ריק בצעד Build | המשתנה לא נשמר ל-`$GITHUB_ENV` | `echo "TAG=..." >> "$GITHUB_ENV"` בצעד קודם |

---

## שאלות לראיון עבודה

**1. מה ההבדל בין CI ל-CD?**
ה-CI הוא בדיקה ובנייה אוטומטית של כל שינוי, מיד אחרי ה-push, כדי לגלות תקלות מוקדם. CD הוא ההמשך: Continuous Delivery אומר שכל שינוי שעבר את הבדיקות מוכן להתקנה, ו-Continuous Deployment אומר שגם ההתקנה קורית לבד.

**2. מה ההבדל בין job ל-step?**
כל step הוא צעד אחד: פקודה או action. job הוא קבוצת צעדים שרצה על runner אחד, לפי הסדר. jobs שונים רצים במקביל, כל אחד על runner משלו, אלא אם כתבנו `needs`.

**3. מה ההבדל בין `uses` ל-`run`?**
השדה `run` מריץ פקודת shell שכתבנו. `uses` מפעיל action מוכן שמישהו פרסם, למשל `actions/checkout`. תמיד עם גרסה אחרי `@`.

**4. למה לתייג image לפי ה-commit, ולא `latest`?**
תגית של commit לא משתנה: יודעים בדיוק איזה קוד רץ, ואפשר לחזור לגרסה קודמת. `latest` זז בכל push, אז אי אפשר לדעת מה רץ, ו-node שכבר הוריד `latest` ישן לא יוריד את החדש.

**5. איך שומרים סיסמה ש-pipeline צריך?**
ב-Secrets של הריפו, לא בקובץ. ב-workflow קוראים לו `${{ secrets.NAME }}`. GitHub מסתיר אותו בלוג, ולא שולח אותו ל-PR מ-fork.

**6. מה זה `GITHUB_TOKEN`, ולמה צריך `permissions`?**
מפתח זמני ש-GitHub מייצר לכל ריצה, רק לריפו הזה. כברירת מחדל הוא מוגבל, ו-`permissions` מוסיף בדיוק את מה שצריך, למשל `packages: write`. העיקרון: הרשאה מינימלית.

**7. מה זה matrix?**
דרך להריץ את אותו job כמה פעמים, עם ערך אחר בכל פעם, במקביל. אצלנו: שלושה סרוויסים, job אחד.

**8. ה-pipeline אדום. מה את עושה?**
נכנסת לריצה, מוצאת את ה-job וה-step האדומים, וקוראת את הלוג מלמטה למעלה. מתקנת, עושה push, ובודקת שהוא ירוק. לא מדלגת על הבדיקה.

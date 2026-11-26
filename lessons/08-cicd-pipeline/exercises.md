# שיעור 8 — תרגולים לבית

**לא מוגש.** התרגולים מכינים לשיעורי הבית. כל תרגול בנוי על הקודם, אז כדאי לפי הסדר.

**איך לעבוד:** לנסות לבד. נתקעתן? לפתוח את **הפתרון** מתחת לתרגיל. אבל קודם לנסות, גם אם לא בטוחות.

**מה צריך:** הריפו שלכן ב-GitHub, עם Actions מופעל (המדריך, "לפני שמתחילות"). ולתרגול 6 גם Docker Desktop עם Kubernetes.

---

## תרגול 1 — לקרוא workflow (על הנייר, 10 דקות)

הנה workflow של מישהי אחרת. לא להריץ. רק לקרוא, ולענות.

```yaml
name: Website

on:
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python3 -m py_compile site/*.py

  docs:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building docs"

  publish:
    needs: check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: echo "Publishing"
```

1. כמה jobs יש כאן? כמה steps בכל אחד?
2. היא עשתה push ל-branch בשם `feature`. מה ירוץ?
3. היא עשתה push ל-`main`. אילו jobs מתחילים יחד, בשנייה הראשונה?
4. `check` נכשל. מה קורה ל-`docs`? ומה ל-`publish`?
5. ב-job `docs` אין `checkout`. האם `ls` שם היה מראה את הקבצים מהריפו?

<details>
<summary>פתרון</summary>

1. שלושה jobs: `check` עם 2 steps, `docs` עם step אחד, `publish` עם 2 steps.
2. כלום. `branches: [main]` אומר רק על push ל-`main`.
3. `check` ו-`docs` יחד. אין להם `needs`, אז הם רצים במקביל. `publish` מחכה ל-`check`.
4. `docs` רץ כרגיל, הוא לא תלוי ב-`check`. `publish` לא ירוץ: הוא יסומן **skipped**, כי יש לו `needs: check`.
5. לא. ה-runner מתחיל ריק. בלי `actions/checkout`, אין בו את הקוד.

</details>

---

## תרגול 2 — hello, ומה הסדר עושה (15 דקות)

1. ליצור בריפו `.github/workflows/hello.yml`, בדיוק כמו בשלב 2 במדריך. commit ו-push.
2. בלשונית Actions: לפתוח את הריצה, ואת הצעד `What is in the repo?`. מה הוא מדפיס?
3. עכשיו להזיז את הצעד `Get the code` להיות **האחרון** ברשימה. push. מה `ls` מדפיס עכשיו? למה?
4. להוסיף ל-`on:` גם `workflow_dispatch`, ולהריץ את ה-workflow מהכפתור **Run workflow**, בלי push.

<details>
<summary>פתרון</summary>

2. את התיקיות והקבצים בשורש הריפו: `app`, `helm`, `lessons`, `README.md` וכו'.

3. כלום. `ls` רץ לפני ה-checkout, והמטבח עדיין ריק. הסדר של ה-steps הוא הסדר שבו הם רצים.

4. כשיש יותר מ-event אחד, `on:` הופך לרשימה:

```yaml
on:
  push:
  workflow_dispatch:
```

ואז בלשונית Actions, משמאל, לבחור `Hello`. מימין מופיע **Run workflow**.

</details>

---

## תרגול 3 — מצאו את הטעות (15 דקות)

בכל אחד מהקבצים יש טעות אחת. מה היא, ומה GitHub יגיד?

**א.**

```yaml
name: A
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check backend
        uses: python3 -m py_compile app/backend/*.py
```

**ב.**

```yaml
name: B
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin
      - run: docker build -t ghcr.io/rivkak/shoplist-backend:v1 app/backend
      - run: docker push ghcr.io/rivkak/shoplist-backend:v1
```

**ג.**

```yaml
name: C
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: TAG=${GITHUB_SHA::7}
      - run: docker build -t shoplist-backend:$TAG app/backend
```

**ד.** הקובץ נשמר בנתיב `github/workflows/ci.yml`.

<details>
<summary>פתרון</summary>

**א.** `uses` במקום `run`. `uses` מצפה לשם של action, בצורה `owner/name@version`. GitHub ייתן שגיאה על הקובץ, משהו כמו `invalid value for uses`. התיקון: `run: python3 -m py_compile ...`.

**ב.** חסר `permissions: packages: write`. ה-login יצליח, אבל ה-push ייכשל עם `denied: permission_denied: write_package`. התיקון, מעל `jobs:`:

```yaml
permissions:
  contents: read
  packages: write
```

**ג.** כל `run` הוא shell חדש. המשתנה `TAG` נעלם בסוף הצעד הראשון, ובצעד השני הוא ריק. התגית תהיה `shoplist-backend:` ו-Docker ייכשל עם `invalid reference format`. התיקון: `echo "TAG=${GITHUB_SHA::7}" >> "$GITHUB_ENV"`.

**ד.** חסרה הנקודה: `.github/workflows/`. GitHub לא יריץ כלום, ולא יגיד כלום.

</details>

---

## תרגול 4 — בקרת איכות שעובדת (20 דקות)

1. ליצור `.github/workflows/ci.yml` עם job אחד, `test`, בדיוק כמו בשלב 5 במדריך. push, ולוודא ✓ ירוק.
2. לשבור את ה-backend: למחוק נקודתיים בסוף שורת `def` ב-`app/backend/app.py`. push.
3. בלוג: באיזה step זה נכשל? איזו שורה? מה ה-exit code?
4. לתקן, ולשבור משהו אחר: ב-`helm/shoplist/values.yaml`, להזיז שורה אחת רווח שמאלה, כך שההזחה תישבר. push. מה `helm lint` אומר?
5. לתקן, ולוודא ירוק.

<details>
<summary>פתרון</summary>

3. ב-`Backend - Python syntax check`. הלוג מראה את שם הקובץ, את מספר השורה, ו-`SyntaxError: expected ':'`. בסוף: `Process completed with exit code 1`. הצעדים אחריו לא רצו.

4. `helm lint` נכשל בצעד `Chart - helm lint`, עם הודעה כמו `unable to parse YAML` ומספר שורה ב-`values.yaml`. אותו צעד שתופס טעויות לפני ש-`helm install` נכשל באמצע.

</details>

---

## תרגול 5 — matrix ו-needs (20 דקות)

1. להשלים את `ci.yml` לגרסה המלאה, כמו בשלב 9 במדריך. push.
2. בדף הריצה: לצייר על דף את הגרף. מי רץ קודם? מי רץ יחד?
3. לפתוח את **Packages** בדף הריפו. כמה packages יש? אילו תגיות יש לכל אחד?
4. לשבור את ה-backend שוב, ולעשות push. מה קורה לשלושת ה-build? האם התגית החדשה הגיעה ל-Packages?
5. לתקן. ואז: להוסיף ל-matrix סרוויס רביעי, `docs`, שאין לו תיקייה. מה יקרה? (לנחש קודם, ואז לנסות. ואחר כך להחזיר)

<details>
<summary>פתרון</summary>

2. `test` לבד. אחריו `build (backend)`, `build (stats)`, `build (frontend)` יחד.

3. שלושה: `shoplist-backend`, `shoplist-stats`, `shoplist-frontend`. לכל אחד שתי תגיות: 7 תווים של ה-commit, ו-`latest`.

4. `test` אדום, ושלושת ה-build **skipped**, באפור. ב-Packages אין תגית חדשה. `latest` עדיין מצביע על ה-image הקודם, הטוב.

5. `build (docs)` ייכשל בצעד Build: `unable to prepare context: path "app/docs" not found`. ושני דברים מעניינים: (א) שלושת ה-build האחרים ממשיכים? לא בהכרח. כברירת מחדל, כשעותק אחד ב-matrix נכשל, GitHub מבטל את העותקים שעוד רצים (`fail-fast`). (ב) ה-images שכבר הספיקו לעלות, נשארים ב-Packages.

</details>

---

## תרגול 6 — מהמחסן אל ה-cluster (20 דקות)

1. להפוך את שלושת ה-packages ל-**Public** (המדריך, שלב 11).
2. `docker pull` ל-backend, עם התגית מהריצה האחרונה. עובד בלי login?
3. ליצור `helm/shoplist/values-registry.yaml`, ולהחליף `OWNER` בשם שלכן, באותיות קטנות.
4. `helm upgrade --install` עם שלוש התגיות (המדריך, שלב 14).
5. לבדוק איזה image רץ ב-backend. ושהאפליקציה עובדת ב-`localhost:30080`.
6. **בונוס:** לשנות משהו קטן ב-frontend (למשל כותרת), push, לחכות לירוק, ו-`helm upgrade` עם התגית החדשה. השינוי מופיע בדפדפן? ואז `helm rollback shop -n shop`. הוא נעלם?

<details>
<summary>פתרון</summary>

2. כן. אם מקבלות `denied`, ה-package עדיין פרטי.

5. 

```shell
kubectl get deploy backend -n shop -o jsonpath='{.spec.template.spec.containers[0].image}'
```

צפוי: `ghcr.io/<השם שלכן>/shoplist-backend:<התגית>`.

6. כן ו-כן. ה-rollback מחזיר את התגית הקודמת, וה-image הקודם עדיין במחסן. בדיוק בגלל זה תגית של commit: כל גרסה נשמרת, עם שם קבוע.

**ה-release `shop` כבר קיים משיעור 7, עם images מקומיים?** זה בסדר. `upgrade` מחליף אותם בתגיות מה-registry. וה-PVC של postgres נשאר, עם המוצרים.

</details>

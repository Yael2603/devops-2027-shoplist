# שיעור 7 — Helm: ShopList באריזה אחת
## מדריך לסטודנטית

---

## מה יהיה בסוף השיעור

- בתיקייה `helm/shoplist/` בריפו: chart אחד, שמתאר את כל ShopList
- ShopList שנייה רצה ב-cluster, ליד זו משיעור 6: אחת ב-`localhost:30080`, ואחת ב-`localhost:30081`
- היסטוריה של גרסאות, וחזרה לגרסה קודמת בפקודה אחת
- ב-chart: מקום מובטח ותקרה לכל container, וגיבוי לילי של מסד הנתונים

**מה תדעו לעשות:**
- להסביר מה זה chart, values ו-release, ולמה Helm קיים
- להפוך קובץ YAML רגיל לתבנית, עם `{{ .Values... }}`
- לבדוק תבנית לפני התקנה, עם `helm lint` ו-`helm template`
- להתקין, לעדכן, לחזור אחורה ולהסיר: `install`, `upgrade`, `rollback`, `uninstall`
- להסביר מי מנצח כשאותו ערך מופיע בכמה מקומות
- להסביר מה עושים requests ו-limits, ומה זה `OOMKilled`
- להסביר מתי משתמשים ב-Job, ב-CronJob, ב-StatefulSet וב-HPA, ולמה לא ב-Deployment

**איך השיעור עובד:** בשיעור אני מדגימה, ואתן עוקבות במדריך הזה. את הכל מתרגלות בבית, ב-[exercises.md](exercises.md). התרגולים לא מוגשים, אבל מכינים לשיעורי הבית.

**עוד לא:** את ה-images אנחנו עדיין בונות ידנית, והפקודות מוקלדות ידנית. בשיעור 8 ה-pipeline יעשה את שניהם.

---

## לפני שמתחילות

- [ ] Docker Desktop פתוח, ולמטה כתוב **Engine running** וגם **Kubernetes running**
- [ ] בתיקייה הראשית של הריפו: `cd devops-2027-shoplist`
- [ ] יש לכן את התיקייה `kubernetes/` משיעור 6, עם 12 הקבצים. אין? הכל מופיע במלואו בהמשך המדריך, אפשר להתחיל גם בלעדיה
- [ ] שלושת ה-images קיימים: `docker images shoplist-*`. אין? לבנות לפי שלב 1 במדריך של שיעור 6
- [ ] Helm מותקן:

```shell
helm version
```

**צפוי:** שורה שמתחילה ב-`version.BuildInfo{Version:"v4.`. מספר הגרסה יכול להיות אחר, העיקר שמתחיל ב-4 (או 3, גם עובד).

**אין Helm?** במחשב בבית:

| מערכת | פקודה |
|---|---|
| Windows | `winget install Helm.Helm`, ואז **לסגור ולפתוח מחדש** את הטרמינל |
| Mac | `brew install helm` |

> **kubectl מדבר עם ה-cluster הנכון?** `kubectl config current-context` צריך להחזיר `docker-desktop`. Helm משתמש באותו חיבור בדיוק.

---

## חלק 1 — למה Helm?

### הבעיה: 12 קבצים, וכל ערך כתוב ביד

בשיעור 6 כתבנו 12 קבצים. עכשיו ההנהלה מבקשת: "תקימי עוד עותק של ShopList, לבדיקות, ליד הקיים".

מה צריך לשנות כדי שזה יעבוד?

| מה | איפה | כמה פעמים |
|---|---|---|
| `namespace: shoplist` | כמעט בכל קובץ | 11 |
| `nodePort: 30080` | frontend-service | 1 (אחרת שתי האפליקציות ינסו את אותה דלת) |
| `replicas` | בשלושה Deployments | 3, אם רוצים מספר אחר |
| הסיסמה | ב-Secret (ב-base64), וגם בבדיקה של postgres | 2, ושניהם חייבים להתאים |

להעתיק את התיקייה ולשנות ביד 17 מקומות. ובטוח שוכחים אחד.

ויש עוד שתי בעיות:

1. **סביבות.** במחשב: `replicas: 1`. בייצור: `replicas: 3`. אותם קבצים, מספרים אחרים. שתי תיקיות כמעט זהות, שעם הזמן מתרחקות זו מזו.
2. **אין "בטלי".** `kubectl apply` לא זוכר מה היה אתמול. שינוי שבר משהו? צריך לזכור מה היה, ולתקן ביד.

### Helm: מנהל החבילות של Kubernetes

אתן כבר מכירות מנהלי חבילות:

| כלי | מתקין | פקודה |
|---|---|---|
| `pip` | ספריות Python | `pip install flask` |
| `winget` | תוכנות ב-Windows | `winget install Helm.Helm` |
| **`helm`** | **אפליקציות שלמות ב-Kubernetes** | `helm install shop ./helm/shoplist` |

ההבדל: `pip` מתקין קובץ אחד. Helm מתקין **אפליקציה שלמה**: כל ה-Deployments, ה-Services, ה-Secrets וה-PVC, יחד, כיחידה אחת עם שם.

> **השם:** Kubernetes ביוונית זה "הקברניט", מי שמנווט את הספינה. Helm זה **ההגה**.

### המשפט של היום

> **התבנית קבועה. מה שמשתנה, גר ב-values.**

---

## חלק 2 — מושגים חדשים

### האנלוגיה: בית דפוס להזמנות

כל זוג שמתחתן מזמין הזמנות. בבית הדפוס לא מעצבים הזמנה חדשה לכל זוג. יש **עיצוב אחד עם קווים ריקים**:

```
  ~ הנכם מוזמנים לחתונה של ________ ו-________ ~
       ביום ________, באולם ________
```

כל זוג ממלא **טופס פרטים**. בית הדפוס ממזג את הטופס לתוך העיצוב, ומדפיס.

| בבית הדפוס | ב-Helm | ב-ShopList |
|---|---|---|
| העיצוב עם הקווים הריקים | **templates** | 11 הקבצים משיעור 6, עם חורים |
| הקו הריק `________` | `{{ .Values.... }}` | `replicas: {{ .Values.backend.replicas }}` |
| טופס הפרטים | **values.yaml** | `replicas: 1`, `nodePort: 30080` |
| העיצוב + הטופס, בתיקייה אחת | **chart** | התיקייה `helm/shoplist/` |
| "תראי לי לפני שמדפיסים" | `helm template` | מדפיס את ה-YAML המוכן למסך, בלי להתקין |
| ההזמנות של זוג מסוים | **release** | `shop`: עותק מותקן אחד, עם שם |
| הדפסה מתוקנת (שינו את השעה) | `helm upgrade`, **revision** חדש | revision 2 |
| "חזרו להדפסה הקודמת" | `helm rollback` | חוזרים ל-revision 1 |

**שלוש המילים שצריך לזכור:**

- **chart:** התבנית. תיקייה עם קבצים. אפשר להתקין אותה הרבה פעמים.
- **values:** הערכים שממלאים בתבנית. יש ברירת מחדל, ואפשר לדרוס.
- **release:** התקנה אחת של chart, עם שם, ב-namespace. כל שינוי בה מקבל מספר: **revision**.

> **טעות נפוצה:** "chart" ו-"release" זה לא אותו דבר. מ-chart אחד אפשר להתקין שלושה releases: `shop`, `shop-test`, `shop-demo`. כמו עיצוב אחד, ושלושה זוגות.

### המבנה של chart

```
helm/
  shoplist/                    ← ה-chart. שם התיקייה = שם ה-chart
    Chart.yaml                 ← תעודת הזהות: שם וגרסה
    values.yaml                ← טופס הפרטים: ערכי ברירת המחדל
    templates/                 ← העיצוב: 11 הקבצים משיעור 6, עם חורים
      postgres-secret.yml
      postgres-configmap.yml
      postgres-pvc.yml
      postgres-deployment.yml
      postgres-service.yml
      backend-deployment.yml
      backend-service.yml
      stats-deployment.yml
      stats-service.yml
      frontend-deployment.yml
      frontend-service.yml
```

**חסר `namespace.yml`?** בכוונה. את ה-namespace בוחרים בזמן ההתקנה, עם `-n`. בהמשך נראה למה.

### הסוגריים המסולסלים: איך קוראים חור

```yaml
replicas: {{ .Values.backend.replicas }}
```

| החלק | מה הוא אומר |
|---|---|
| `{{ ... }}` | "כאן יש חור. Helm, תמלא אותו" |
| `.Values` | "תחפש בטופס הפרטים", ב-`values.yaml` |
| `.backend.replicas` | הכתובת בתוך הטופס: המגירה `backend`, ובתוכה `replicas` |

ובטופס, `values.yaml`:

```yaml
backend:          ← המגירה
  replicas: 1     ← מה שבתוכה
```

הכתובת `.Values.backend.replicas` עוקבת אחרי ההזחה ב-`values.yaml`, קומה אחרי קומה. כל נקודה היא "להיכנס פנימה".

> **טעות נפוצה:** אות אחת שגויה בכתובת. `{{ .Values.backend.replica }}` (בלי s) לא נותן שגיאה. Helm פשוט משאיר את החור ריק, ו-Kubernetes משתמש בברירת המחדל שלו. לכן תמיד מסתכלות על התוצאה עם `helm template`.

### ערכים מובנים: `.Release`

חוץ מ-`.Values`, ל-Helm יש ערכים שהוא ממלא לבד, מתוך פקודת ההתקנה:

| ערך | מה הוא | דוגמה |
|---|---|---|
| `{{ .Release.Namespace }}` | ה-namespace מהפקודה, `-n` | `shop-helm` |
| `{{ .Release.Name }}` | השם שנתנו להתקנה | `shop` |
| `{{ .Release.Revision }}` | מספר הגרסה של ההתקנה | `1`, `2`, `3` |

**למה `.Release.Namespace` ולא `.Values.namespace`?** כי ההזמנה לא כותבת על עצמה לאיזו עיר לשלוח. את זה כותבים **על המעטפה**, ברגע השליחה. אותו chart, ו-`-n` שונה בכל התקנה.

### צינור: `|`

```yaml
POSTGRES_PASSWORD: {{ .Values.postgres.password | b64enc | quote }}
```

הערך עובר דרך **צינור**, משמאל לימין, וכל תחנה עושה לו משהו:

```
shoppass  →  b64enc  →  c2hvcHBhc3M=  →  quote  →  "c2hvcHBhc3M="
```

- `b64enc`: מקודד ל-base64. בשיעור 6 עשינו את זה ביד ב-PowerShell. עכשיו Helm עושה את זה לבד, וב-`values.yaml` הסיסמה כתובה רגיל.
- `quote`: עוטף במירכאות, כדי ש-YAML יבין שזה טקסט.

> **שימו לב:** base64 עדיין לא הצפנה (שיעור 6). ובעבודה אמיתית, סיסמה אמיתית לא נכנסת ל-`values.yaml` בגיט. מעבירים אותה בזמן ההתקנה, עם `--set`.

### Helm מדביק מדבקת בעלות

כש-Helm יוצר משאב, הוא מדביק עליו מדבקה: "שייך ל-release `shop`". זוכרות את המדבקות על המגשים משיעור 6? אותו רעיון.

- **Helm נוגע רק במשאבים עם המדבקה שלו.** משאב שנוצר עם `kubectl apply` אין לו מדבקה, ו-Helm יסרב לגעת בו.
- **ההיסטוריה נשמרת ב-cluster עצמו:** כל revision נשמר כ-Secret באותו namespace, בשם כמו `sh.helm.release.v1.shop.v1`. זה הקלסר של בית הדפוס.

### מה קורה בתוך `helm install`, צעד אחר צעד

```
values.yaml ─┐
-f / --set ──┼─► 1. ממזג ──► 2. ממלא חורים ──► 3. שולח ל-cluster ──► 4. שומר בקלסר
templates/ ──┘    ערכים      (= helm template)     (כמו kubectl apply)     (Secret של revision)
```

1. **ממזג ערכים:** `values.yaml`, ואז קבצי `-f`, ואז `--set`. מי שאחרון מנצח.
2. **ממלא חורים:** בדיוק מה ש-`helm template` מראה.
3. **שולח ל-cluster:** אותו API ש-`kubectl apply` מדבר איתו. מכאן Kubernetes עושה את מה שהוא תמיד עושה: Deployment, ReplicaSet, pods.
4. **שומר בקלסר:** מה ביקשנו ומה נשלח, כ-revision חדש.

> **Helm לא רץ בתוך ה-cluster.** הוא תוכנה במחשב שלכן, כמו `kubectl`. הוא מכין YAML, שולח, ורושם. מי שמריץ את ה-pods זה עדיין Kubernetes.

---

## חלק 3 — בונים את ה-chart

**הקצב:** כל חור מתחיל במושג, ואז ממלאות אותו בקובץ. בהתחלה יחד, בסוף לבד.

### שלב 1 — Chart.yaml: תעודת הזהות

יוצרות את התיקיות:

**ב-PowerShell:**
```powershell
mkdir helm\shoplist\templates
```

**ב-Git Bash:**
```shell
mkdir -p helm/shoplist/templates
```

**`helm/shoplist/Chart.yaml`:**

```yaml
apiVersion: v2
name: shoplist
description: ShopList - frontend, backend, stats and postgres
type: application
version: 0.1.0
appVersion: "1.0.0"
```

| שדה | מה זה |
|---|---|
| `apiVersion: v2` | הפורמט של charts. `v2` הוא הנוכחי, גם ב-Helm 4 |
| `name` | שם ה-chart. כמו שם התיקייה |
| `version` | הגרסה **של ה-chart**, של התבנית. משנים קובץ ב-`templates/`? מעלים ל-`0.2.0` |
| `appVersion` | הגרסה **של האפליקציה** בפנים. רק מידע, לקריאה |

> **טעות נפוצה:** לבלבל בין `version` ל-`appVersion`. `version` זה העיצוב של ההזמנה. `appVersion` זה הזוג. אפשר לשנות עיצוב בלי להחליף זוג, ולהפך.

### שלב 2 — chart בלי חורים

מעתיקות את 11 הקבצים משיעור 6 לתוך `templates/`. **בלי** `namespace.yml`.

**ב-PowerShell:**
```powershell
Copy-Item kubernetes\*.yml helm\shoplist\templates\
Remove-Item helm\shoplist\templates\namespace.yml
```

**ב-Git Bash:**
```shell
cp kubernetes/*.yml helm/shoplist/templates/
rm helm/shoplist/templates/namespace.yml
```

ויוצרות `helm/shoplist/values.yaml` **ריק**. עוד אין לנו מה לשים בו.

ועכשיו: תצוגה לפני הדפסה.

```shell
helm template shop ./helm/shoplist
```

**צפוי:** כל 11 הקבצים, מודפסים למסך, בדיוק כמו שכתבנו אותם. כל קובץ מתחיל בשורה `# Source: shoplist/templates/...`.

> **כבר יש לנו chart.** הוא עדיין לא עושה שום דבר חכם: אין בו חורים. אבל ראינו את העיקרון: **Helm לא ממציא YAML. הוא רק ממלא חורים ומדפיס.** כל מה שיגיע ל-cluster, אפשר לראות קודם.

**`helm template` לא מתקין כלום.** הוא לא מדבר עם ה-cluster בכלל. אפשר להריץ אותו כמה פעמים שרוצים.

### שלב 3 — החור הראשון: namespace

בכל 11 הקבצים, משנות את השורה:

```yaml
  namespace: shoplist
```

ל:

```yaml
  namespace: {{ .Release.Namespace }}
```

> **ב-VS Code:** `Ctrl+Shift+H` (חיפוש והחלפה בכל הקבצים). בשדה "files to include" לכתוב `helm/shoplist/templates`. לחפש `namespace: shoplist`, להחליף ב-`namespace: {{ .Release.Namespace }}`.

בודקות:

```shell
helm template shop ./helm/shoplist -n shop-helm
```

**צפוי:** בכל הקבצים, `namespace: shop-helm`. תריצו שוב עם `-n banana`. ה-chart לא השתנה, התוצאה כן.

### שלב 4 — ה-backend: replicas ו-image

**קודם הטופס.** `helm/shoplist/values.yaml`:

```yaml
imagePullPolicy: Never

backend:
  replicas: 1
  image:
    repository: shoplist-backend
    tag: local
```

**ועכשיו החורים.** ב-`templates/backend-deployment.yml`, שלוש שורות משתנות:

```yaml
spec:
  replicas: {{ .Values.backend.replicas }}
```

```yaml
          image: {{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}
          imagePullPolicy: {{ .Values.imagePullPolicy }}
```

<details>
<summary>הקובץ המלא: <code>templates/backend-deployment.yml</code></summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: {{ .Release.Namespace }}
spec:
  replicas: {{ .Values.backend.replicas }}
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: {{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}
          imagePullPolicy: {{ .Values.imagePullPolicy }}
          env:
            - name: DB_HOST
              value: postgres
            - name: DB_NAME
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_DB
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_USER
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
          ports:
            - containerPort: 5000
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
```

</details>

**למה לפצל את ה-image לשניים, `repository` ו-`tag`?** כי הם משתנים בקצב אחר. השם `shoplist-backend` כמעט לא משתנה. התגית משתנה בכל גרסה חדשה. בשיעור 8, ה-pipeline ישנה **רק** את ה-`tag`, בפקודה אחת.

**למה `imagePullPolicy` בקומה העליונה, ולא בתוך `backend`?** כי הוא אותו דבר לכל שלושת ה-images. ערך משותף לכולם, פעם אחת.

בודקות, ומסתכלות רק על הקובץ הזה:

```shell
helm template shop ./helm/shoplist --show-only templates/backend-deployment.yml
helm template shop ./helm/shoplist --show-only templates/backend-deployment.yml --set backend.replicas=3
```

**צפוי:** בפעם הראשונה `replicas: 1`, בשנייה `replicas: 3`. **`--set` דורס ערך מהטופס, רק לפקודה הזו.**

### שלב 5 — stats ו-frontend: אותה תבנית

> **בבית:** זה תרגול 1 ב-[exercises.md](exercises.md). לנסות למלא לבד, לפני שפותחות את הפתרון.

אותה תבנית בדיוק. מה שונה: ל-frontend יש עוד חור אחד, ה-`nodePort`.

**1. משלימות את `values.yaml`.** מתחת ל-backend:

```yaml
stats:
  replicas: ____
  image:
    repository: ____
    tag: ____

frontend:
  replicas: 1
  nodePort: ____
  image:
    repository: ____
    tag: ____
```

**2. משלימות את החורים בקבצים:**

| קובץ | שורה | החור |
|---|---|---|
| `stats-deployment.yml` | `replicas:` | `{{ .Values.stats.____ }}` |
| `stats-deployment.yml` | `image:` | `{{ .Values.stats.image.____ }}:{{ ____ }}` |
| `stats-deployment.yml` | `imagePullPolicy:` | כמו ב-backend |
| `frontend-deployment.yml` | שלוש השורות | כמו ב-stats, עם `frontend` |
| `frontend-service.yml` | `nodePort:` | `{{ ____ }}` |

**3. בודקות:**

```shell
helm template shop ./helm/shoplist | findstr "image: replicas: nodePort:"
```

(ב-Git Bash: `| grep -E "image:|replicas:|nodePort:"`)

**צפוי:** שלושה images עם `:local`, ארבע שורות `replicas: 1`, ו-`nodePort: 30080`.

> **למה `nodePort` חייב להיות חור?** כי הוא הדלת מבחוץ, והיא **אחת לכל ה-cluster**. שתי התקנות עם אותו `nodePort` לא יכולות לחיות ביחד. Kubernetes יגיד: `provided port is already allocated`.

<details>
<summary>נתקעתן? <code>values.yaml</code> המלא עד עכשיו</summary>

```yaml
imagePullPolicy: Never

backend:
  replicas: 1
  image:
    repository: shoplist-backend
    tag: local

stats:
  replicas: 1
  image:
    repository: shoplist-stats
    tag: local

frontend:
  replicas: 1
  nodePort: 30080
  image:
    repository: shoplist-frontend
    tag: local
```

</details>

<details>
<summary>נתקעתן? <code>templates/frontend-service.yml</code></summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: {{ .Release.Namespace }}
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
      nodePort: {{ .Values.frontend.nodePort }}
```

</details>

### שלב 6 — postgres: הסיסמה, פעם אחת

בשיעור 6 שם המשתמש הופיע בשני מקומות: ב-Secret (ב-base64), ובבדיקה `pg_isready`. משנים באחד ושוכחים את השני? postgres לא מוכן לנצח.

**עכשיו: ערך אחד בטופס, ושני חורים שקוראים ממנו.**

מוסיפות ל-`values.yaml`:

```yaml
postgres:
  database: shoplist
  user: shopuser
  password: shoppass
  storage: 1Gi
```

**`templates/postgres-secret.yml`:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: {{ .Release.Namespace }}
type: Opaque
data:
  POSTGRES_DB: {{ .Values.postgres.database | b64enc | quote }}
  POSTGRES_USER: {{ .Values.postgres.user | b64enc | quote }}
  POSTGRES_PASSWORD: {{ .Values.postgres.password | b64enc | quote }}
```

**ב-`templates/postgres-deployment.yml`,** שורת הבדיקה:

```yaml
              command: ["pg_isready", "-U", {{ .Values.postgres.user | quote }}, "-d", {{ .Values.postgres.database | quote }}]
```

בודקות:

```shell
helm template shop ./helm/shoplist --show-only templates/postgres-secret.yml
```

**צפוי:** `POSTGRES_PASSWORD: "c2hvcHBhc3M="`. בדיוק מה שכתבנו ביד בשיעור 6.

### שלב 7 — הארונית: גודל, ופתק "לא לפנות"

**`templates/postgres-pvc.yml`:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: {{ .Release.Namespace }}
  annotations:
    helm.sh/resource-policy: keep
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {{ .Values.postgres.storage }}
```

**מה זה `helm.sh/resource-policy: keep`?** כשמסירים release עם `helm uninstall`, Helm מוחק **כל** מה שהוא יצר. כולל הארונית, וכולל כל המוצרים. הפתק הזה אומר לו: "את זה לא לפנות". ה-PVC נשאר, והנתונים איתו.

> **annotations מול labels:** שתיהן מדבקות. **labels** משמשות לחיפוש ולבחירה (ה-selector של ה-Service). **annotations** הן פתקים עם מידע לכלים אחרים. Kubernetes לא מחפש לפיהן.

### שלב 8 — בדיקה לפני הדפסה

שתי בדיקות, לפני כל התקנה:

```shell
helm lint ./helm/shoplist
helm template shop ./helm/shoplist -n shop-helm
```

| פקודה | כמו | מה היא בודקת |
|---|---|---|
| `helm lint` | מגיהה | שהמבנה תקין: Chart.yaml, YAML חוקי, חורים שאפשר למלא |
| `helm template` | תצוגה לפני הדפסה | מה בדיוק יגיע ל-cluster. **הכי חשוב להסתכל** |

**צפוי מ-`lint`:** `1 chart(s) linted, 0 chart(s) failed`. ההודעה `[INFO] Chart.yaml: icon is recommended` היא רק המלצה. מתעלמות.

<details>
<summary>כל הקבצים המלאים של ה-chart (למי שצריכה להשוות)</summary>

**`helm/shoplist/values.yaml`**

```yaml
imagePullPolicy: Never

backend:
  replicas: 1
  image:
    repository: shoplist-backend
    tag: local

stats:
  replicas: 1
  image:
    repository: shoplist-stats
    tag: local

frontend:
  replicas: 1
  nodePort: 30080
  image:
    repository: shoplist-frontend
    tag: local

postgres:
  database: shoplist
  user: shopuser
  password: shoppass
  storage: 1Gi
```

**`templates/stats-deployment.yml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stats
  namespace: {{ .Release.Namespace }}
spec:
  replicas: {{ .Values.stats.replicas }}
  selector:
    matchLabels:
      app: stats
  template:
    metadata:
      labels:
        app: stats
    spec:
      containers:
        - name: stats
          image: {{ .Values.stats.image.repository }}:{{ .Values.stats.image.tag }}
          imagePullPolicy: {{ .Values.imagePullPolicy }}
          env:
            - name: BACKEND_URL
              value: http://backend:5000
          ports:
            - containerPort: 3000
          readinessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
```

**`templates/frontend-deployment.yml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: {{ .Release.Namespace }}
spec:
  replicas: {{ .Values.frontend.replicas }}
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: {{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}
          imagePullPolicy: {{ .Values.imagePullPolicy }}
          ports:
            - containerPort: 80
```

**`templates/postgres-deployment.yml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: {{ .Release.Namespace }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          envFrom:
            - secretRef:
                name: postgres-secret
          ports:
            - containerPort: 5432
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", {{ .Values.postgres.user | quote }}, "-d", {{ .Values.postgres.database | quote }}]
            initialDelaySeconds: 5
            periodSeconds: 10
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
            - name: postgres-init
              mountPath: /docker-entrypoint-initdb.d
      volumes:
        - name: postgres-data
          persistentVolumeClaim:
            claimName: postgres-pvc
        - name: postgres-init
          configMap:
            name: postgres-init
```

**ארבעת ה-Services ו-ConfigMap של init.sql:** בדיוק כמו בשיעור 6, רק עם `namespace: {{ .Release.Namespace }}`. ב-`frontend-service.yml` גם `nodePort: {{ .Values.frontend.nodePort }}`.

</details>

---

## חלק 4 — Helm בפעולה: חיים של release

### שלב 9 — install: ShopList שנייה, בפקודה אחת

ShopList משיעור 6 עדיין רצה ב-namespace `shoplist`, בדלת 30080. מתקינות לידה עותק שני:

```shell
helm install shop ./helm/shoplist -n shop-helm --create-namespace --set frontend.nodePort=30081
```

| חלק | מה הוא אומר |
|---|---|
| `install shop` | התקנה חדשה, בשם `shop` (שם ה-release) |
| `./helm/shoplist` | מאיזה chart. כאן: תיקייה מקומית |
| `-n shop-helm` | לאיזה namespace. זה `.Release.Namespace` |
| `--create-namespace` | אם ה-namespace לא קיים, ליצור אותו. במקום `namespace.yml` |
| `--set frontend.nodePort=30081` | דלת אחרת. 30080 כבר תפוסה |

**צפוי:** `STATUS: deployed`, `REVISION: 1`, ומתחת ההוראות מתוך `NOTES.txt` אם יש.

```shell
kubectl get pods -n shop-helm -w
```

כשכולם `1/1 Running`: לפתוח `http://localhost:30081`. ובכרטיסייה אחרת `http://localhost:30080`.

**שתי ShopList, זו לצד זו.** כל אחת עם מסד נתונים משלה: מוצר שמוסיפים באחת לא מופיע בשנייה. מ-chart אחד.

> **שאלה לפני שמריצות:** מה היה קורה בלי `--set frontend.nodePort=30081`?
> <details><summary>תשובה</summary>ההתקנה נכשלת: <code>provided port is already allocated</code>. הדלת 30080 תפוסה על ידי ShopList משיעור 6. NodePort הוא אחד לכל ה-cluster, גם בין namespaces.</details>

> **ושאלה שנייה:** ומה היה קורה עם `-n shoplist`, ה-namespace של שיעור 6?
> <details><summary>תשובה</summary>ההתקנה נכשלת: <code>exists and cannot be imported into the current release</code>. ה-Service <code>postgres</code> כבר קיים שם, ואין עליו מדבקת בעלות של Helm. Helm לא דורס משאב שהוא לא יצר.</details>

### שלב 10 — מה Helm יודע

```shell
helm list -A
helm status shop -n shop-helm
helm get values shop -n shop-helm
kubectl get secrets -n shop-helm
```

| פקודה | מה רואים |
|---|---|
| `helm list -A` | כל ה-releases בכל ה-namespaces. `-A` = all |
| `helm status shop` | מצב ה-release, ו-revision נוכחי |
| `helm get values shop` | מה **אנחנו** ביקשנו: `frontend: nodePort: 30081`. רק מה שדרסנו |
| `kubectl get secrets` | `postgres-secret`, וגם `sh.helm.release.v1.shop.v1`: הקלסר. כאן Helm שומר את ההיסטוריה |

> **chart לעומת release:** `helm list` לא מראה charts. הוא מראה **התקנות**. ה-chart הוא רק תיקייה במחשב שלכן.

### שלב 11 — upgrade: מה שלא כתבת, חוזר לברירת המחדל

רוצות 3 עותקים של ה-backend. מה לדעתכן יקרה בפקודה הזו? **רק לחשוב, לא להריץ:**

```shell
# לא להריץ
helm upgrade shop ./helm/shoplist -n shop-helm --set backend.replicas=3
```

<details>
<summary>תשובה</summary>

העדכון נכשל עם `provided port is already allocated`, וב-`helm history` נרשם revision עם `STATUS: failed`. **ב-upgrade, כל מה שלא כתוב בפקודה חוזר לערך מ-`values.yaml`.** לא ביקשנו שוב `nodePort=30081`, אז Helm החזיר אותו ל-30080, ששייכת לשיעור 6.

כמו בבית הדפוס: כל הזמנה היא **הזמנה מלאה**. מה שלא כתבת בטופס, מקבל את ברירת המחדל. לא "כמו בפעם הקודמת".

</details>

**הפתרון: טופס משלכן, בקובץ.** יוצרות `helm/shoplist/values-test.yaml`:

```yaml
frontend:
  nodePort: 30081

backend:
  replicas: 3
```

כותבות רק **מה ששונה** מ-`values.yaml`. כל השאר נלקח משם.

```shell
helm upgrade shop ./helm/shoplist -n shop-helm -f helm/shoplist/values-test.yaml
kubectl get pods -n shop-helm
```

**צפוי:** `REVISION: 2`, ושלושה pods של backend.

> **למה קובץ ולא `--set`?** קובץ נשמר בגיט, ואפשר לראות בדיוק מה ביקשנו. `--set` נשכח. כלל אצבע: `--set` לבדיקה מהירה או לסוד. כל השאר בקובץ.

### מי מנצח? סדר העדיפויות

כשאותו ערך מופיע בכמה מקומות:

| מקום | דוגמה | עדיפות |
|---|---|---|
| `values.yaml` בתוך ה-chart | `replicas: 1` | נמוכה: ברירת מחדל |
| קובץ עם `-f` | `values-test.yaml`: `replicas: 3` | דורס את `values.yaml` |
| `--set` | `--set backend.replicas=5` | **הכי גבוהה** |

**מי שמדבר אחרון, מנצח.** ברירת המחדל של בית הדפוס, אחריה הטופס שהזוג מילא, ואחרון הטלפון של הרגע האחרון.

אפשר כמה `-f`: `-f values-test.yaml -f values-big.yaml`. האחרון בשורה מנצח.

### שלב 12 — לשבור, ולחזור אחורה

שוברות בכוונה: image שלא קיים.

```shell
helm upgrade shop ./helm/shoplist -n shop-helm -f helm/shoplist/values-test.yaml --set backend.image.tag=oops
kubectl get pods -n shop-helm
```

**צפוי:** pod חדש של backend ב-`ErrImageNeverPull`. **אבל:** שלושת ה-pods הישנים עדיין `Running`, והאפליקציה ב-30081 עדיין עובדת!

> **למה האפליקציה לא נפלה?** זוכרות את readinessProbe משיעור 6? Kubernetes מעדכן בהדרגה: מעלה pod חדש, מחכה שיהיה מוכן, ורק אז מוריד ישן. ה-pod החדש אף פעם לא מוכן, אז הישנים לא יורדים.

עכשיו ההיסטוריה:

```shell
helm history shop -n shop-helm
```

(בקיצור, בלי חלק מהעמודות:)

```
REVISION  STATUS      DESCRIPTION
1         superseded  Install complete
2         superseded  Upgrade complete
3         deployed    Upgrade complete
```

וחוזרות לגרסה 2, האחרונה שעבדה:

> **המספרים אצלכן שונים?** אם הרצתן בטעות את הפקודה משלב 11, יש אצלכן revision נוסף עם `failed`. מחפשות ב-`helm history` את ה-revision האחרון שבו ה-image תקין, וחוזרות **אליו**.

```shell
helm rollback shop 2 -n shop-helm
helm history shop -n shop-helm
```

**צפוי:** revision **4**, עם `Rollback to 2`. ה-pod השבור נעלם.

> **למה 4 ולא 2?** כי היסטוריה לא נמחקת. כמו "היסטוריית גרסאות" ב-Google Docs: שחזור גרסה ישנה יוצר גרסה חדשה, שהתוכן שלה זהה לישנה. כך תמיד רואים מה קרה, ומתי.

> **`helm rollback shop` בלי מספר** חוזר לגרסה אחת אחורה.

### שלב 13 — uninstall, והארונית שנשארה

```shell
helm uninstall shop -n shop-helm
kubectl get all -n shop-helm
kubectl get pvc -n shop-helm
```

**צפוי:** אין pods, אין Services. אבל **ה-PVC עדיין שם**, בזכות הפתק `keep`.

מתקינות שוב, עם אותו שם:

```shell
helm install shop ./helm/shoplist -n shop-helm -f helm/shoplist/values-test.yaml
```

**צפוי:** ב-`localhost:30081` המוצרים שהוספתן קודם עדיין שם. האפליקציה חדשה, הארונית ישנה.

> **`helm uninstall` לעומת `kubectl delete namespace`:** `uninstall` מוחק רק מה שיש עליו מדבקה של ה-release, ומכבד את הפתק `keep`. מחיקת namespace מוחקת **הכל** בתוכו, כולל ה-PVC, בלי לשאול.

> **ה-namespace עצמו** (`shop-helm`) נשאר אחרי `uninstall`. Helm לא מוחק namespace שנוצר עם `--create-namespace`.

### בבית: מחזור חיים שלם, לבד

install, upgrade, לשבור, rollback ו-uninstall, על release שלישי בדלת 30082: תרגול 2 ב-[exercises.md](exercises.md).

---

## חלק 5 — מילון פקודות

| מה רוצות | kubectl (שיעור 6) | Helm |
|---|---|---|
| לראות מה יותקן, בלי להתקין | אין | `helm template shop ./helm/shoplist` |
| לבדוק שהקבצים תקינים | אין | `helm lint ./helm/shoplist` |
| להתקין | `kubectl apply -f kubernetes/` | `helm install shop ./helm/shoplist -n <ns> --create-namespace` |
| לשנות ערך | לערוך קובץ, ו-`apply` שוב | `helm upgrade shop ./helm/shoplist -n <ns> -f <file>` |
| מה מותקן | `kubectl get all -n <ns>` | `helm list -A` |
| מה ביקשתי | לפתוח את הקבצים | `helm get values shop -n <ns>` |
| היסטוריה | אין | `helm history shop -n <ns>` |
| לחזור אחורה | אין. לתקן ביד | `helm rollback shop <revision> -n <ns>` |
| להסיר | `kubectl delete -f kubernetes/` | `helm uninstall shop -n <ns>` |

> **אל תערבבו:** release ש-Helm התקין, משנים רק דרך Helm. שינוי ידני עם `kubectl edit` או `kubectl scale` לא נרשם בהיסטוריה, וה-`upgrade` הבא ידרוס אותו.

---

## חלק 6 — ובעולם האמיתי?

### charts מוכנים: חנות האפליקציות

לא כל chart כותבים לבד. לרוב התוכנות המוכרות (מסדי נתונים, ניטור, Ingress Controllers) יש chart מוכן, שמישהו אחר מתחזק. מחפשים ב-**Artifact Hub** (`artifacthub.io`), החנות של Helm.

```shell
helm repo add grafana https://grafana.github.io/helm-charts
helm show values grafana/grafana
helm install monitoring grafana/grafana -n monitoring --create-namespace -f my-values.yaml
```

| פקודה | מה היא עושה |
|---|---|
| `helm repo add` | מוסיפה "חנות" לרשימה. כמו להוסיף מקור התקנה |
| `helm show values` | מראה את טופס הפרטים של ה-chart: מה אפשר לשנות |
| `helm install ... grafana/grafana` | מתקינה ישר מהחנות, עם הטופס שלכן |

> **בעבודה:** קוראים את `helm show values` לפני שמתקינים. שם כתוב מה כל ערך עושה. לא בכיתה: הרשת בכיתה חוסמת חלק מהחנויות.

### Helm ב-pipeline (שיעור 8)

בשיעור 8 ה-pipeline יבנה image חדש עם תגית חדשה בכל push. ואז שורה אחת:

```shell
helm upgrade --install shoplist ./helm/shoplist -n shoplist --create-namespace -f values-prod.yaml --set backend.image.tag=a1b2c3d
```

**`upgrade --install`:** "אין release כזה? תתקיני. יש? תעדכני." אותה פקודה בפעם הראשונה ובפעם המאה. בדיוק מה ש-pipeline צריך.

וזה הרגע שבו הפיצול של `image` ל-`repository` ול-`tag` משתלם: ה-pipeline משנה רק את ה-`tag`.

### מתי Helm, ומתי לא

| מצב | מה מתאים |
|---|---|
| לומדות, או משהו קטן וחד-פעמי | קבצי YAML ו-`kubectl apply` |
| אותה אפליקציה בכמה סביבות, או כמה עותקים | **Helm** |
| צריך היסטוריה ו-rollback | **Helm** |
| מתקינות תוכנה מוכרת (Grafana, Prometheus) | **Helm**, עם chart מוכן |

> **רק לדעת שקיים:** **Kustomize** הוא כלי אחר לאותה בעיה, שבנוי בתוך `kubectl` (`kubectl apply -k`). בלי חורים: לוקחים YAML רגיל ומדביקים עליו שינויים לכל סביבה. בלי היסטוריה ובלי rollback.

---

## חלק 7 — משאבים מתקדמים ב-Kubernetes

עד עכשיו השתמשנו ב-Deployment, Service, ConfigMap, Secret ו-PVC. יש עוד כמה משאבים שכל מי שעובדת עם Kubernetes פוגשת. את כולם מכניסות לאותו chart, כחורים חדשים ב-`values.yaml`.

| משאב | מה הוא פותר | אנלוגיה |
|---|---|---|
| `resources` (requests ו-limits) | כמה CPU וזיכרון כל container מקבל | מקום שמור במטבח, ותקרה |
| Job | משימה שרצה פעם אחת ונגמרת | הזמנה חד-פעמית: עוגת יום הולדת |
| CronJob | Job שרץ לפי שעון | משימה ביומן המטבח: ספירת מלאי כל לילה |
| StatefulSet | pods עם שם קבוע ודיסק משלהם, למסדי נתונים | מגשים ממוספרים, לכל מגש ארונית משלו |
| HorizontalPodAutoscaler | מוסיף ומוריד pods לפי עומס | לפני חג: עוד מגשים כשההזמנות נערמות |

### requests ו-limits: מקום שמור במטבח, ותקרה

**הבעיה:** כל node הוא מטבח, ובכל מטבח הרבה מגשים (pods). בלי מידע, הסדרנית (ה-scheduler) לא יודעת כמה מקום כל מגש צריך. מגש אחד יכול לתפוס את כל הזיכרון של המטבח, ולהפיל את כל השכנים.

**האנלוגיה: המטבח של הקונדיטוריה.**
- **requests** = מקום שמור. המקום **מובטח** למגש. הסדרנית (ה-scheduler) שולחת מגש רק למטבח שנשאר בו מספיק מקום, לפי מה שכל המגשים שם כבר שמרו.
- **limits** = התקרה. **CPU** הוא זמן תנור: מגש שרוצה יותר מהחלק שלו, מחכה בתור לתנור ומאט (throttling). **זיכרון** הוא מקום על השיש: מגש שמתפרס מעבר למקום שלו, נזרק. ה-container נהרג (`OOMKilled`), ו-Kubernetes מכין אותו מחדש.

```yaml
          resources:
            requests:
              cpu: 100m        # 100 millicores = עשירית ליבה
              memory: 128Mi
            limits:
              cpu: 500m        # חצי ליבה
              memory: 256Mi
```

| יחידה | פירוש |
|---|---|
| `1` או `1000m` | ליבת CPU אחת |
| `100m` | עשירית ליבה (m = אלפית) |
| `128Mi` | 128 מגה-בייט (Mi = 1024×1024) |
| `1Gi` | גיגה-בייט אחד |

**ב-chart:** לכל סרוויס מגירה `resources` ב-`values.yaml`, ובתבנית חורים:

```yaml
          resources:
            requests:
              cpu: {{ .Values.backend.resources.requests.cpu | quote }}
              memory: {{ .Values.backend.resources.requests.memory }}
            limits:
              cpu: {{ .Values.backend.resources.limits.cpu | quote }}
              memory: {{ .Values.backend.resources.limits.memory }}
```

> **למה `quote` על cpu?** כי `"1"` הוא טקסט, ו-`1` בלי מירכאות הוא מספר. Kubernetes מקבל את שניהם, אבל `quote` שומר שהתוצאה תמיד אחידה.

**ההדגמה בשיעור: OOMKilled.** נותנות ל-backend תקרה קטנה מדי:

```shell
helm upgrade shop ./helm/shoplist -n shop-helm -f helm/shoplist/values-test.yaml --set backend.resources.limits.memory=20Mi
kubectl get pods -n shop-helm -w
kubectl describe pod -n shop-helm -l app=backend      # Last State: Terminated, Reason: OOMKilled
helm rollback shop -n shop-helm
```

**צפוי:** pod חדש של backend ב-`OOMKilled` ואחר כך `CrashLoopBackOff`. הישנים ממשיכים לעבוד, בזכות readinessProbe. ו-rollback מחזיר את הכל. כל מה שלמדנו היום, ביחד.

> **בעבודה:** limits לזיכרון תמיד. limits ל-CPU, תלוי בצוות: יש מי שמוותרות עליו, כדי לא להאט סתם. requests תמיד, כי בלעדיהם ה-scheduler מנחש.

### Job ו-CronJob: משימה שנגמרת

**הבעיה:** Deployment דואג שה-pod **תמיד** ירוץ. אם הוא מסתיים, Deployment מקים אותו שוב. אבל יש משימות שאמורות להיגמר: גיבוי, הסבת נתונים, שליחת דוח. אם נריץ אותן ב-Deployment, הן ירוצו שוב ושוב לנצח.

| משאב | מתי רץ | מה קורה בסוף |
|---|---|---|
| Deployment | תמיד | ה-pod מסתיים? מקימים שוב |
| **Job** | פעם אחת | ה-pod מסתיים בהצלחה, והעבודה גמורה. נכשל? מנסה שוב, עד `backoffLimit` |
| **CronJob** | לפי שעון | בכל פעם שהשעה מגיעה, יוצר Job חדש |

**האנלוגיה:** Deployment היא ההזמנה הקבועה משיעור 5: תמיד שלושה מגשים על הדלפק, נגמר מגש מכינים חדש. Job היא הזמנה חד-פעמית, כמו עוגת יום הולדת: אופים, מגישים, וההזמנה נסגרת. נשרפה? אופים שוב. CronJob היא משימה ביומן המטבח: "כל לילה ב-02:00, ספירת מלאי במקרר".

**הזמנים של CronJob:** חמישה שדות, כמו ב-Linux:

```
"0 2 * * *"
 │ │ │ │ └─ יום בשבוע (0 = ראשון)
 │ │ │ └─── חודש
 │ │ └───── יום בחודש
 │ └─────── שעה
 └───────── דקה
```

| ביטוי | מתי |
|---|---|
| `0 2 * * *` | כל לילה ב-02:00 |
| `*/15 * * * *` | כל רבע שעה |
| `0 9 * * 0` | כל יום ראשון ב-09:00 |

> **שעון של מי?** של ה-cluster, ובדרך כלל זה UTC. 02:00 UTC הוא 04:00 או 05:00 בישראל.

**ב-ShopList: גיבוי לילי של המוצרים.** CronJob שמריץ `pg_dump` ושומר את הקובץ בארונית נפרדת:

```yaml
{{- if .Values.backup.enabled }}
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup
  namespace: {{ .Release.Namespace }}
spec:
  schedule: {{ .Values.backup.schedule | quote }}
  successfulJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: postgres:15-alpine
              envFrom:
                - secretRef:
                    name: postgres-secret
              command:
                - sh
                - -c
                - |
                  set -e
                  FILE=/backup/shoplist-$(date +%Y%m%d-%H%M).sql
                  PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h postgres -U "$POSTGRES_USER" "$POSTGRES_DB" > "$FILE"
                  echo "backup saved: $FILE"
                  ls -lh /backup
              volumeMounts:
                - name: backup
                  mountPath: /backup
          volumes:
            - name: backup
              persistentVolumeClaim:
                claimName: backup-pvc
{{- end }}
```

שלושה דברים חדשים בקובץ:

1. **`{{- if .Values.backup.enabled }}` ... `{{- end }}`:** חור מסוג חדש. **תנאי**. אם `backup.enabled` הוא `true`, הקובץ כולו נכנס. אם `false`, הוא לא קיים בכלל. כך כל התקנה בוחרת אם היא רוצה גיבוי. המקף ב-`{{-` מוחק את השורה הריקה שהתנאי משאיר.
2. **`jobTemplate` בתוך `template`:** CronJob יוצר Job, וה-Job יוצר pod. שלוש קומות, כמו Deployment שיוצר ReplicaSet שיוצר pods.
3. **`restartPolicy: OnFailure`:** ב-Deployment זה תמיד `Always`. ב-Job: אם נכשל, לנסות שוב. אם הצליח, לא לעשות כלום.

וגם קובץ `backup-pvc.yml`: ארונית נפרדת לגיבויים, עם אותו `if` ואותו פתק `keep`.

**ההדגמה בשיעור:** לא מחכים לשתיים בלילה. יוצרות Job מה-CronJob, עכשיו:

```shell
kubectl get cronjob -n shop-helm
kubectl create job backup-now --from=cronjob/backup -n shop-helm
kubectl get jobs,pods -n shop-helm
kubectl logs job/backup-now -n shop-helm
```

**צפוי:** ה-pod עובר ל-`Completed`, ה-Job ל-`1/1`, ובלוג: `backup saved: /backup/shoplist-....sql`, ורשימת הקבצים בארונית.

> **`Completed` זה טוב.** ב-Deployment, pod שנגמר הוא תקלה. ב-Job, זו המטרה.

### StatefulSet: לכל pod שם וארונית משלו

**הבעיה:** ב-Deployment, כל ה-pods זהים ואפשר להחליף אותם: `backend-7f9c...`, `backend-a2b1...`. שם אקראי, ואין להם דיסק משלהם. ל-backend זה מושלם. למסד נתונים עם כמה עותקים, לא: כל עותק צריך **את הנתונים שלו**, ושם קבוע שאפשר לפנות אליו ("הראשי הוא postgres-0").

**האנלוגיה:** pods של Deployment הם מגשים זהים: כל מגש מחליף כל מגש. pods של StatefulSet הם מגשים ממוספרים: מגש 0, מגש 1, ולכל מגש ארונית משלו עם אותו מספר. מגש 1 נשרף? המגש החדש מקבל שוב את המספר 1, ואת ארונית 1 עם כל מה שבתוכה.

| | Deployment | StatefulSet |
|---|---|---|
| שמות ה-pods | אקראיים: `backend-7f9c...` | קבועים, לפי מספר: `postgres-0`, `postgres-1` |
| דיסק | ארונית אחת משותפת (או בלי) | ארונית **לכל pod**, מ-`volumeClaimTemplates` |
| סדר עלייה | כולם בבת אחת | אחד אחרי השני: 0, ואז 1, ואז 2 |
| pod שנמחק | חוזר עם שם חדש | חוזר עם **אותו שם ואותה ארונית** |
| מתאים ל | backend, frontend, stats | מסדי נתונים, Kafka, Elasticsearch |

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres          # Service מיוחד, "headless", שנותן כתובת לכל pod
  replicas: 1
  ...
  volumeClaimTemplates:          # במקום PVC אחד: טופס שממנו נוצר PVC לכל pod
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

> **למה ב-ShopList נשארנו עם Deployment?** כי יש לנו postgres אחד, עם ארונית אחת. זה עובד. StatefulSet משתלם כשיש כמה עותקים של מסד נתונים. **ובעבודה:** לרוב לא כותבים StatefulSet למסד נתונים לבד. משתמשים ב-chart מוכן או ב-Operator, או במסד מנוהל של הענן (כמו RDS), כמו שראינו בשיעור 6.

### HorizontalPodAutoscaler: עוד מגשים לפני חג

**הבעיה:** `replicas: 3` זה מספר קבוע. בשתיים בלילה זה בזבוז. לפני חג, כשההזמנות נערמות, אולי לא מספיק.

**האנלוגיה:** המטבח לפני חג. כשההזמנות נערמות, מוסיפים מגשים. כשנרגע, מורידים. HPA עושה את זה ל-pods: מודד את העומס כל כמה שניות, ומשנה את `replicas` של ה-Deployment לבד.

```yaml
{{- if .Values.backend.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend
  namespace: {{ .Release.Namespace }}
spec:
  scaleTargetRef:                 # את מי מגדילים
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: {{ .Values.backend.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.backend.autoscaling.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.backend.autoscaling.cpuPercent }}
{{- end }}
```

**`averageUtilization: 70`:** אחוז **מה-requests**. אם requests הוא `100m`, ה-HPA מוסיף pods כשהממוצע עובר `70m`. **ולכן: בלי requests, אין HPA.** הנה למה requests חשוב.

**HPA צריך מישהו שמודד:** `metrics-server`. בענן הוא כמעט תמיד מותקן. ב-Docker Desktop לא, ולכן ב-chart שלנו `autoscaling.enabled: false`. בלעדיו, `kubectl get hpa` מראה `<unknown>` במקום אחוזים.

> **אל תערבבו:** אם יש HPA, הוא שולט ב-`replicas`. ה-`replicas` שכתוב ב-Deployment רק קובע את ההתחלה.

### המפה: כל המשאבים של ShopList עכשיו

| משאב | ב-ShopList | למה |
|---|---|---|
| Deployment | postgres, backend, stats, frontend | pods שתמיד רצים |
| Service | ארבעה | כתובת קבועה |
| Secret | `postgres-secret` | סיסמאות |
| ConfigMap | `postgres-init` | `init.sql` |
| PVC | `postgres-pvc`, `backup-pvc` | נתונים שנשארים |
| resources | בכל container | מקום מובטח ותקרה |
| CronJob | `backup` | גיבוי כל לילה |
| HPA | `backend`, כבוי כברירת מחדל | הגדלה לפי עומס |
| StatefulSet | לא בשימוש | מכירות, ויודעות למה לא כאן |

---

## תקלות נפוצות

| בעיה | סיבה | פתרון |
|---|---|---|
| `helm: command not found` / `'helm' is not recognized` | Helm לא מותקן, או שהטרמינל נפתח לפני ההתקנה | לסגור ולפתוח את הטרמינל. `helm version` |
| `Kubernetes cluster unreachable` | Kubernetes לא רץ, או context אחר | Docker Desktop: **Kubernetes running**. `kubectl config current-context` |
| `nil pointer evaluating interface {}.tag` | שגיאת כתיב באמצע הכתובת: `.Values.backend.imag.tag` | השגיאה אומרת קובץ ושורה. להשוות לקומות ב-`values.yaml` |
| `replicas:` ריק ב-`helm template` | שגיאת כתיב בסוף הכתובת: `.Values.backend.replica` | אין שגיאה! רק `helm template` מגלה. להשוות לשם ב-`values.yaml` |
| `error converting YAML to JSON` / `mapping values are not allowed` | הזחה שגויה, או Tab | רווחים בלבד. ב-`helm lint` כתוב באיזו שורה |
| `provided port is already allocated` | ה-`nodePort` תפוס בהתקנה אחרת | `--set frontend.nodePort=30081`, או בקובץ values |
| `cannot re-use a name that is still in use` | כבר יש release בשם הזה | `helm list -A`. שם אחר, או `helm upgrade` במקום `install` |
| `exists and cannot be imported into the current release` | המשאב נוצר עם `kubectl apply`, בלי מדבקה של Helm | להתקין ל-namespace אחר. או למחוק קודם את הישן (מוחק נתונים!) |
| release ב-`STATUS: failed` | ה-install או ה-upgrade נכשל באמצע | לתקן, ו-`helm upgrade` שוב. או `helm uninstall` ולהתחיל מחדש |
| upgrade "החזיר" ערך ישן | ערך שהועבר ב-`--set` בפעם הקודמת, ולא הפעם | ערכים קבועים בקובץ `-f`, לא ב-`--set` |
| `ErrImageNeverPull` | tag שלא קיים, או images לא נבנו | `docker images shoplist-*`. `helm rollback` |
| `OOMKilled`, ואחר כך `CrashLoopBackOff` | ה-container עבר את תקרת הזיכרון (`limits.memory`) | להגדיל את ה-limit ב-values. `kubectl describe pod`: `Last State: OOMKilled` |
| pod תקוע ב-`Pending`, ובאירועים `Insufficient cpu` או `Insufficient memory` | ה-requests גדולים ממה שיש ב-node | להקטין את ה-requests, או פחות replicas |
| `kubectl get hpa` מראה `<unknown>/70%` | אין `metrics-server`, או שאין `requests.cpu` ל-container | תרגול 5 ב-[exercises.md](exercises.md). ולבדוק שיש `resources.requests.cpu` |
| ה-CronJob לא רץ בשעה שציפיתן | השעון של ה-cluster הוא UTC | לחשב לפי UTC. ולבדיקה: `kubectl create job ... --from=cronjob/backup` |
| pod של backup ב-`Error` | סיסמה, שם ה-Service או ה-PVC לא תואמים | `kubectl logs job/<שם>`. לבדוק את שלושת השמות: `postgres-secret`, `postgres`, `backup-pvc` |

---

## שאלות לראיון עבודה

**1. מה זה Helm, ואיזו בעיה הוא פותר?**
מנהל חבילות ל-Kubernetes. הוא אורז את כל קבצי ה-YAML של אפליקציה לחבילה אחת (chart), עם ערכים שאפשר לשנות בכל התקנה. הוא פותר שלוש בעיות: שכפול של קבצים כמעט זהים בין סביבות, התקנה של אפליקציה שלמה כיחידה אחת, והיסטוריה עם אפשרות לחזור אחורה.

**2. מה ההבדל בין chart, release ו-revision?**
chart הוא התבנית: תיקייה עם templates ו-values. release הוא התקנה אחת של chart, עם שם, ב-namespace. revision הוא גרסה של release: כל install, upgrade או rollback יוצר revision חדש.

**3. איך דורסים ערכים, ומה סדר העדיפויות?**
`values.yaml` של ה-chart הוא ברירת המחדל. קבצים עם `-f` דורסים אותו, לפי הסדר בשורה. `--set` דורס את כולם. ב-upgrade, כל ערך שלא הועבר שוב חוזר לברירת המחדל, אלא אם משתמשים ב-`--reuse-values`.

**4. מה קורה ב-`helm rollback`, ולמה נוצר revision חדש?**
Helm לוקח את ה-manifests של ה-revision הישן ומחיל אותם שוב. ההיסטוריה לא נמחקת: ה-rollback הוא revision חדש, עם תוכן זהה לישן. כך רואים מה קרה ומתי.

**5. מה קורה ל-PVC ב-`helm uninstall`?**
אם ה-PVC הוא חלק מה-chart, הוא נמחק יחד עם כל השאר, וגם הנתונים. כדי לשמור אותו, מוסיפים לו annotation: `helm.sh/resource-policy: keep`. בעבודה אמיתית, מסד נתונים חשוב בדרך כלל לא נמצא בכלל באותו chart.

**6. איפה Helm שומר את ההיסטוריה?**
בתוך ה-cluster, כ-Secrets באותו namespace של ה-release, בשם כמו `sh.helm.release.v1.<name>.v<revision>`. אין שרת נפרד.

**7. מה ההבדל בין requests ל-limits?**
requests הוא המינימום המובטח: ה-scheduler מציב pod רק ב-node שיש בו מספיק מקום לפי ה-requests. limits הוא התקרה: על CPU מעל התקרה, ה-container מואט. על זיכרון מעל התקרה, הוא נהרג (`OOMKilled`) ומופעל מחדש. ו-HPA מחשב אחוזים מתוך ה-requests.

**8. מה ההבדל בין Deployment, Job ו-CronJob?**
Deployment מחזיק pods שרצים תמיד, ומקים אותם מחדש אם הם נגמרים. Job מריץ משימה עד שהיא מסתיימת בהצלחה, ומנסה שוב אם נכשלה. CronJob יוצר Job לפי לוח זמנים, כמו cron ב-Linux. דוגמה: גיבוי לילי.

**9. מתי StatefulSet ולא Deployment?**
כשכל pod צריך זהות קבועה: שם קבוע (`postgres-0`), ארונית משלו (`volumeClaimTemplates`), ועלייה לפי הסדר. מתאים למסדי נתונים ולמערכות מבוזרות כמו Kafka. לאפליקציות בלי מצב, כמו backend, Deployment עדיף.

**10. איך HPA מחליט כמה pods צריך?**
הוא קורא מדדים מ-`metrics-server`, משווה את הממוצע ליעד (למשל 70% מה-requests של CPU), ומשנה את `replicas` של ה-Deployment, בין המינימום למקסימום. הוא מגדיל מהר, ומקטין לאט, כדי לא לקפוץ הלוך וחזור.

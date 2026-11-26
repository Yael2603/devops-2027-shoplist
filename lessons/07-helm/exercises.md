# שיעור 7 — תרגולים

## לתרגל בבית, אחרי השיעור

בשיעור ראיתן הדגמה של כל מה שכאן. עכשיו תורכן, בקצב שלכן.

**איך לעבוד:**
- התרגולים לפי הסדר. כל אחד נשען על הקודם
- קודם לנסות לבד. הפתרון מקופל מתחת לכל תרגיל, ופותחים אותו רק אחרי ניסיון
- בכל תרגיל כתוב **מה אמור לקרות**. אם קרה משהו אחר, זה הזמן לחפש בטבלת התקלות במדריך

**השמות בתרגולים:** release בשם `shop`, ב-namespace `shop-helm`, כמו במדריך. בנתם בשם אחר? להחליף בכל הפקודות.

> **התרגולים לא מוגשים.** מה שמוגש הוא [homework.md](homework.md). אבל מי שעושה את התרגולים, שיעורי הבית ייקחו לה חצי מהזמן.

---

## תרגול 1 — stats ו-frontend: אותה תבנית (10 דקות)

**המטרה:** לבד, להפוך עוד שני Deployments לתבנית.

במדריך, שלב 5: להשלים את הקווים הריקים ב-`values.yaml`, ב-`stats-deployment.yml`, ב-`frontend-deployment.yml` וב-`frontend-service.yml`. בלי להציץ בפתרון שבמדריך.

**מה אמור לקרות:**

```shell
helm lint ./helm/shoplist
helm template shop ./helm/shoplist -n shop-helm | findstr /C:"replicas:" /C:"image:" /C:"nodePort:"
```

(ב-Mac: `grep -E "replicas:|image:|nodePort:"` במקום `findstr`.)

`lint` בלי שגיאות. ב-`template`: לכל `replicas:` יש מספר, לכל `image:` יש שם ותגית, ו-`nodePort: 30080`.

---

## תרגול 2 — מחזור חיים שלם (15 דקות)

**המטרה:** release שלישי, לבד, מההתחלה ועד הסוף.

1. `install` של release בשם `shop-demo`, ב-namespace `shop-demo`, בדלת **30082**
2. לפתוח את `localhost:30082` ולהוסיף מוצר
3. `upgrade` עם `stats.replicas=2`. **בלי לאבד את הדלת 30082** (רמז: קובץ)
4. `helm history`: צריך לראות 2 revisions
5. לשבור את ה-frontend: tag שלא קיים
6. `rollback`. כמה revisions יש עכשיו?
7. `uninstall`, ולבדוק שה-PVC נשאר

<details>
<summary>הפתרון</summary>

`helm/shoplist/values-demo.yaml`:

```yaml
frontend:
  nodePort: 30082
stats:
  replicas: 2
```

```shell
helm install shop-demo ./helm/shoplist -n shop-demo --create-namespace --set frontend.nodePort=30082
helm upgrade shop-demo ./helm/shoplist -n shop-demo -f helm/shoplist/values-demo.yaml
helm history shop-demo -n shop-demo
helm upgrade shop-demo ./helm/shoplist -n shop-demo -f helm/shoplist/values-demo.yaml --set frontend.image.tag=oops
helm rollback shop-demo -n shop-demo
helm history shop-demo -n shop-demo
helm uninstall shop-demo -n shop-demo
kubectl get pvc -n shop-demo
```

אחרי ה-rollback: 4 revisions.

</details>

---

## תרגול 3 — requests ו-limits, ו-OOMKilled (15 דקות)

**המטרה:** לתת ל-backend מקום שמור במטבח ותקרה, ולראות מה קורה כשהתקרה נמוכה מדי.

**1. ב-`values.yaml`,** בתוך המגירה של `backend`, להוסיף:

```yaml
  resources:
    requests:
      cpu: ____        # a tenth of a core
      memory: ____     # 128 megabytes
    limits:
      cpu: ____        # half a core
      memory: ____     # 256 megabytes
```

**2. ב-`backend-deployment.yml`,** בתוך ה-container, באותה הזחה של `ports:`, להוסיף בלוק `resources:` עם ארבעה חורים, שקוראים מהמגירה החדשה. ל-cpu להוסיף `| quote`.

**3. לבדוק ולעדכן:**

```shell
helm template shop ./helm/shoplist -n shop-helm -s templates/backend-deployment.yml
helm upgrade shop ./helm/shoplist -n shop-helm -f helm/shoplist/values-test.yaml
kubectl describe pod -n shop-helm -l app=backend
```

**מה אמור לקרות:** ב-`describe`, תחת ה-container, שני חלקים חדשים: `Limits` ו-`Requests`, עם הערכים שכתבתן.

**4. לשבור:** תקרת זיכרון קטנה מדי.

```shell
helm upgrade shop ./helm/shoplist -n shop-helm -f helm/shoplist/values-test.yaml --set backend.resources.limits.memory=20Mi
kubectl get pods -n shop-helm -w
```

**מה אמור לקרות:** pod חדש של backend, שעובר ל-`OOMKilled`, ואחר כך ל-`CrashLoopBackOff`. ה-pods הישנים ממשיכים לעבוד, והאפליקציה בדפדפן עדיין עובדת. למה? (רמז: readinessProbe, שיעור 6.)

**5. לחזור:** `helm rollback shop -n shop-helm`, ולבדוק שאין יותר pod שבור.

<details>
<summary>הפתרון</summary>

`values.yaml`:

```yaml
backend:
  # ... replicas and image stay as they were
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi
```

`backend-deployment.yml`, בתוך ה-container:

```yaml
          resources:
            requests:
              cpu: {{ .Values.backend.resources.requests.cpu | quote }}
              memory: {{ .Values.backend.resources.requests.memory }}
            limits:
              cpu: {{ .Values.backend.resources.limits.cpu | quote }}
              memory: {{ .Values.backend.resources.limits.memory }}
```

ב-`kubectl describe pod`, אחרי השבירה:

```
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
```

</details>

**להמשך:** אותו דבר ל-stats, ל-frontend ול-postgres. הערכים: בטבלה שבמדריך, חלק 7.

---

## תרגול 4 — גיבוי לילי: CronJob (20 דקות)

**המטרה:** משימה ביומן המטבח שמגבה כל לילה את מסד הנתונים, ולהפעיל אותו עכשיו, בלי לחכות ללילה.

**1. ב-`values.yaml`,** מגירה חדשה, בקומה הראשונה (לא בתוך סרוויס):

```yaml
backup:
  enabled: true
  schedule: "0 2 * * *"
  storage: 1Gi
```

**2. `templates/backup-pvc.yml`:** ארונית לגיבויים. להעתיק את `postgres-pvc.yml`, ולשנות: את השם ל-`backup-pvc`, ואת הגודל ל-`{{ .Values.backup.storage }}`. לעטוף את כל הקובץ בתנאי:

```yaml
{{- if .Values.backup.enabled }}
# ... the whole PVC here
{{- end }}
```

**3. `templates/backup-cronjob.yml`:** להעתיק מהמדריך, חלק 7, את ה-CronJob המלא. לקרוא אותו עם ארבע השאלות, ולענות לעצמכן:
- מה זה? (kind)
- איך קוראים לו?
- מה הוא רוצה? (מתי, ומה הפקודה)
- את מי הוא מוצא? (שלושה שמות שמגיעים מקבצים אחרים. מצאתן את שלושתם?)

**4. לבדוק את התנאי:**

```shell
helm template shop ./helm/shoplist -n shop-helm | findstr "kind:"
helm template shop ./helm/shoplist -n shop-helm --set backup.enabled=false | findstr "kind:"
```

**מה אמור לקרות:** בראשון יש `kind: CronJob` ועוד `PersistentVolumeClaim`. בשני, הם נעלמו.

**5. להתקין ולהפעיל עכשיו:**

```shell
helm upgrade shop ./helm/shoplist -n shop-helm -f helm/shoplist/values-test.yaml
kubectl get cronjob -n shop-helm
kubectl create job backup-now --from=cronjob/backup -n shop-helm
kubectl get jobs,pods -n shop-helm
kubectl logs job/backup-now -n shop-helm
```

**מה אמור לקרות:** ה-Job ב-`1/1`, ה-pod ב-`Completed`, ובלוג: `backup saved: /backup/shoplist-....sql`.

**6. השעון:** לשנות את `schedule` ל-`"*/2 * * * *"` (כל שתי דקות), `upgrade`, ולחכות חמש דקות עם `kubectl get jobs -n shop-helm -w`. כמה Jobs נוצרו? אחר כך להחזיר ל-`"0 2 * * *"`.

<details>
<summary>הפתרון</summary>

`templates/backup-pvc.yml`:

```yaml
{{- if .Values.backup.enabled }}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backup-pvc
  namespace: {{ .Release.Namespace }}
  annotations:
    helm.sh/resource-policy: keep
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {{ .Values.backup.storage }}
{{- end }}
```

שלושת השמות ב-CronJob שמגיעים מקבצים אחרים:
1. `postgres-secret`: הסיסמה, המשתמש ושם מסד הנתונים, מ-`postgres-secret.yml`
2. `-h postgres`: הכתובת של מסד הנתונים, שם ה-Service מ-`postgres-service.yml`
3. `backup-pvc`: הארונית, מ-`backup-pvc.yml`

בשלב 6: אחרי חמש דקות, 2 או 3 Jobs. ב-`kubectl get jobs` רואים רק את 3 האחרונים, בגלל `successfulJobsHistoryLimit: 3`.

</details>

---

## תרגול 5 — בונוס: HPA, עוד מגשים לפני חג (20 דקות)

**המטרה:** לראות את Kubernetes מוסיף pods לבד, כשיש עומס.

**1. מישהו שמודד:** ב-Docker Desktop אין `metrics-server`. מתקינות אותו, עם Helm, מהחנות:

```shell
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm install metrics-server metrics-server/metrics-server -n kube-system --set "args={--kubelet-insecure-tls}"
```

> **`--kubelet-insecure-tls`:** רק למחשב שלכן. ב-Docker Desktop התעודות לא חתומות כמו בענן. בענן לא משתמשים בזה.

אחרי דקה:

```shell
kubectl top pods -n shop-helm
```

**מה אמור לקרות:** טבלה עם CPU וזיכרון לכל pod. `error: Metrics API not available`? לחכות עוד דקה.

**2. `templates/backend-hpa.yml`:** להעתיק מהמדריך, חלק 7. ב-`values.yaml`, בתוך `backend`:

```yaml
  autoscaling:
    enabled: true
    minReplicas: 1
    maxReplicas: 5
    cpuPercent: 70
```

**3. עומס:** `upgrade`, ואז, בחלון אחד:

```shell
kubectl get hpa -n shop-helm -w
```

ובחלון שני, pod קטן ששולח בקשות בלי הפסקה:

```shell
kubectl run load -n shop-helm --rm -it --image=busybox:1.36 --restart=Never -- sh -c "while true; do wget -q -O- http://backend:5000/health > /dev/null; done"
```

**מה אמור לקרות:** בחלון הראשון, האחוז עולה מעל `70%`, ו-`REPLICAS` עולה: 2, 3... לעצור את העומס עם `Ctrl+C`. אחרי כחמש דקות, ה-replicas יורדים חזרה ל-1. ירידה לאט זה בכוונה: כדי לא להוריד מגשים ולהוסיף שוב כל דקה.

> **האחוז לא עולה מעל 70?** ה-`/health` קל מאוד. אפשר לפתוח עוד חלון עם עוד `kubectl run load2 ...`, או להוריד את `cpuPercent` ל-`30`.

**4. לסיים:** להחזיר `autoscaling.enabled: false`, ו-`upgrade`.

---

## תרגול 6 — StatefulSet: שאלות על הנייר (10 דקות)

בלי מחשב. לענות בשתי שורות, ואז לפתוח.

1. ב-Deployment של backend עם 3 replicas, pod אחד נמחק. מה יהיה השם של ה-pod שיחליף אותו? ומה אם זה StatefulSet של postgres עם 3 replicas, ונמחק `postgres-1`?
2. למה StatefulSet משתמש ב-`volumeClaimTemplates`, ולא ב-`claimName` אחד כמו ה-Deployment שלנו?
3. ב-ShopList יש postgres אחד, עם Deployment. מתי הייתן עוברות ל-StatefulSet?
4. חברה אומרת: "בואו נשים את ה-backend ב-StatefulSet, כדי שיהיו לו שמות יפים". מה תגידו לה?

<details>
<summary>תשובות</summary>

1. ב-Deployment: שם חדש ואקראי, כמו `backend-7f9c-x2k4p`. ב-StatefulSet: שוב `postgres-1`, עם אותה ארונית, `data-postgres-1`.
2. כי לכל pod צריכה להיות ארונית משלו. `claimName` אחד הוא ארונית אחת לכולם. `volumeClaimTemplates` הוא טופס, וממנו נוצר PVC לכל pod.
3. כשיהיו כמה עותקים של מסד הנתונים: ראשי ומשניים, שכל אחד צריך את הנתונים שלו ושם קבוע. ובעבודה, לרוב לא כותבים אותו לבד: chart מוכן, Operator, או מסד מנוהל בענן.
4. ה-backend לא שומר נתונים. כל pod שלו זהה לאחרים, וזה בדיוק מה ש-Deployment עושה הכי טוב: מחליף, מגדיל ומעדכן בקלות. StatefulSet רק יאט אותו: עולה אחד אחרי השני, ומתעדכן אחד אחרי השני.

</details>

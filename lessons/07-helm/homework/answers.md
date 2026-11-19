# שיעור 7 — Helm: תשובות

> **הערה על הסביבה:** ב-cluster שלי עדיין רצה ShopList משיעור 6 (namespace `shoplist`) על NodePort `30080`, ולכן ב-`values.yaml` הוגדר `frontend.nodePort: 30081`. בדיקת האפליקציה בוצעה דרך `kubectl port-forward -n shop service/frontend 8081:80` (`http://localhost:8081`).

## תוצאות הבדיקות (בקצרה)

- `helm lint ./helm/shoplist` ← `1 chart(s) linted, 0 chart(s) failed`
- `helm template`: כל `namespace:` הוא `shop`, ה-images הם `shoplist-*:local`, `nodePort: 30081`, ו-`pg_isready` מקבל `shopuser` / `shoplist` מתוך values.
- ד4: ארבעה רכיבים `Running`, נוספו מוצרים, backend ו-stats ירוקים (צילום 1).
- ד5: אחרי upgrade עם `values-big.yaml` — backend `3/3`, stats `2/2`.
- ד6: `--set backend.image.tag=missing` ← pod חדש של backend ב-`ErrImageNeverPull`; `helm rollback shop 2` ← 4 revisions, האחרון `Rollback to 2` (צילום 2).
- ד7: אחרי `helm uninstall` ה-PVC `postgres-pvc` נשאר `Bound` (צילום 3). אחרי התקנה מחדש, אותן 5 רשומות (כולל `HelmPersistTest`) עדיין במסד.

## ד6 — האפליקציה עדיין עובדת?

כן. בזמן שה-pod החדש של backend היה ב-`ErrImageNeverPull`, שלושת ה-pods הישנים נשארו `Running`, ו-`/api/health` ו-`/api/products` החזירו תשובה תקינה.

## ד8 — שאלות

**1. מה ההבדל בין chart ל-release? תנו דוגמה מהשיעור.**
chart הוא התבנית (התיקייה `helm/shoplist` עם `Chart.yaml`, `values.yaml` ו-`templates/`). release הוא התקנה אחת בפועל של ה-chart ב-cluster, עם שם, namespace וערכים משלה. מאותו chart `shoplist` אפשר להתקין את ה-release `shop` ב-namespace `shop`, ועוד release `shop2` ב-namespace אחר.

**2. למה הסרנו את `namespace.yml` מה-chart, ומה מחליף אותו?**
כי ה-namespace נבחר בזמן ההתקנה ולא נכתב בתוך ה-chart, כדי שאותו chart יותקן בכל namespace. במקומו: `-n shop --create-namespace` בפקודת ההתקנה, ובתבניות `namespace: {{ .Release.Namespace }}`.

**3. בד5 כתבתן ב-`values-big.yaml` רק שני ערכים. מאיפה הגיעו כל השאר, למשל `nodePort`?**
מ-`values.yaml` של ה-chart. Helm מתחיל מברירות המחדל שבו, ומעליהן דורס רק את מה שכתוב בקובץ `-f` (ומעל זה `--set`). לכן `nodePort: 30081`, ה-images וכל השאר נשארו כמו ב-`values.yaml`.

**4. בד6, האפליקציה עבדה גם כשה-image היה שבור. למה?**
בגלל ה-RollingUpdate של ה-Deployment (שיעור 6): Kubernetes מוריד pod ישן רק אחרי שה-pod החדש מוכן. ה-pod החדש לא עלה (`ErrImageNeverPull`) ולא עבר readiness, ולכן ה-pods הישנים המשיכו לרוץ, וה-Service שלח אליהם את הבקשות.

**5. אחרי ה-rollback יש 4 revisions ולא 2. למה Helm לא פשוט חוזר ל-revision 2?**
כי ההיסטוריה ב-Helm רק מתווספת ולא נמחקת. rollback הוא פעולה חדשה שמתקינה שוב את ההגדרות של revision 2, ולכן נרשם revision 4 עם התיאור `Rollback to 2`. כך נשמר תיעוד מלא של מה שקרה, כולל ה-revision השבור, ואפשר לחזור גם אליו.

**6. מה היה קורה לשלושת המוצרים בד7 בלי השורה `helm.sh/resource-policy: keep`?**
`helm uninstall` היה מוחק גם את ה-PVC, יחד עם ה-volume והנתונים. בהתקנה מחדש היה נוצר PVC ריק, `init.sql` היה יוצר טבלה ריקה, והמוצרים היו נעלמים.

**7. חברה כתבה בטעות `{{ .Values.backend.replica }}`. Helm לא נתן שגיאה. מה כן קרה, ואיך היא הייתה מגלה?**
מפתח שלא קיים ב-values מחזיר ערך ריק, אז נוצרה השורה `replicas:` בלי ערך. Kubernetes מתייחס לזה כאילו השדה לא נכתב ומשתמש בברירת המחדל: pod אחד, במקום הערך מ-`values.yaml`. אפשר לגלות ב-`helm template` (לחפש `replicas:` ריק), או אחרי ההתקנה ב-`kubectl get deploy` שמראה `1/1` במקום `2/2`.

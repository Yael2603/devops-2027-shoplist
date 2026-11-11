# שיעור 6 — תשובות

### 1. למה `shoplist-backend:local` ולא `docker-backend`? ומה בלי `imagePullPolicy: Never`?
השם `docker-backend` הוא שם ש-Compose המציא לפי שם התיקייה, ואינו מתאר את הפרויקט. שם מפורש עם תג קבוע (`local`) מבטיח שה-Deployment מצביע בדיוק על ה-image שבנינו. בלי `imagePullPolicy: Never`, Kubernetes היה מנסה להוריד את ה-image מ-Docker Hub, שבו הוא לא קיים, וה-pod היה נתקע ב-`ErrImagePull` / `ImagePullBackOff`.

### 2. פענוח `POSTGRES_PASSWORD`
```powershell
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("c2hvcHBhc3M="))
```
התוצאה: `shoppass`. Base64 הוא קידוד ולא הצפנה, כך שכל מי שיכול לקרוא את ה-Secret (או את הקובץ ב-Git) יכול לפענח אותו בשנייה. ההגנה של Secret באה מהרשאות הגישה ב-cluster, לא מהקידוד.

### 3. מה שמר את המוצרים אחרי מחיקת ה-pod?
`postgres-pvc.yml`: ה-PVC מחובר ל-`/var/lib/postgresql/data`, והנתונים יושבים עליו ולא בתוך ה-container. ה-pod החדש (`postgres-...-vhvkg`) התחבר לאותו PVC, ו-Milk, Bread ו-Eggs נשארו. הפקודה שכן הייתה מוחקת אותם: `kubectl delete pvc postgres-pvc -n shoplist` (או מחיקת כל ה-namespace).

### 4. אין `depends_on`. מה קורה אם backend עולה לפני postgres?
ה-backend עולה, אבל החיבור למסד נכשל עד ש-postgres מוכן. ה-readinessProbe (`/health`) דואג שה-Service לא ישלח אליו בקשות עד שהבדיקה עוברת, וה-readinessProbe של postgres (`pg_isready`) דואג שה-Service `postgres` לא יקבל תעבורה לפני שמסד הנתונים מוכן. אם container נופל, Kubernetes מרים אותו שוב עד שהכל קיים.

### 5. ד8: selector שגוי (`app: backnd`)
בדפדפן הנורית של backend הפכה לאדומה, ובקשה ל-`/api/health` החזירה `502 Bad Gateway`. ה-pods של backend **לא** נפלו: שניהם נשארו `1/1 Running`. `kubectl get endpoints backend` הראה `<none>`, וב-`describe service` הופיע `Selector: app=backnd` עם `Endpoints:` ריק. הסיבה: ה-Service מוצא pods רק לפי המדבקה, ואף pod לא נושא `app=backnd`, אז אין לו לאן להעביר תעבורה, ו-Nginx קיבל שגיאה. אחרי התיקון ל-`app: backend`, חזרו שתי הכתובות (`10.244.0.12:5000`, `10.244.0.7:5000`) והבדיקה החזירה 200.

### 6. שיניתי את `app-config`, אבל backend רואה את הערך הישן
משתני סביבה נקראים רק כשה-container עולה. `apply` משנה את ה-ConfigMap, אבל לא את ה-pods שכבר רצים. הפתרון: `kubectl rollout restart deployment/backend -n shoplist`, שיוצר pods חדשים שקוראים את הערך החדש.

### 7. כמה פעמים `shoplist`, ומה עם `shoplist-test`?
כשם של namespace, `shoplist` כתוב 12 פעמים ב-12 הקבצים: `namespace: shoplist` ב-11 קבצים, ועוד `name: shoplist` ב-`namespace.yml`. בנוסף הוא מופיע גם ב-`app-config.yml`. כדי להריץ עותק ב-`shoplist-test` צריך לשנות את כל 13 הקבצים. זה בדיוק מה ש-Helm פותר: ערך אחד, במקום אחד, במקום 13 עריכות ידניות.

---

### הערה: `localhost:30080` בסביבת kind
ה-cluster אצלי הוא מסוג kind (`desktop-control-plane`). ב-kind ה-NodePort קיים בתוך ה-container של ה-node, ולא ממופה אוטומטית ל-localhost של Windows, ולכן `http://localhost:30080` החזיר `ERR_CONNECTION_REFUSED` אף שה-Service תקין (`80:30080/TCP`). כדי לגשת לאותה כתובת הרצתי:
```powershell
kubectl port-forward -n shoplist service/frontend 30080:80
```

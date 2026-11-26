# שיעור 7: Helm — ShopList באריזה אחת

## מה לומדות בשיעור

- למה Helm קיים: 12 קבצים, וכל ערך כתוב ביד
- chart, values ו-release: העיצוב, טופס הפרטים, וההזמנות של זוג מסוים
- להפוך YAML רגיל לתבנית: `{{ .Values... }}`, `{{ .Release.Namespace }}`, והצינור `| b64enc`
- `helm lint` ו-`helm template`: לראות מה יותקן, לפני שמתקינים
- `install`, `upgrade`, `history`, `rollback` ו-`uninstall`: החיים של release
- מי מנצח: `values.yaml`, קובץ `-f`, או `--set`
- מה קורה ל-PVC ב-`uninstall`, ואיך שומרים עליו
- משאבים מתקדמים ב-Kubernetes: requests ו-limits, Job ו-CronJob (גיבוי לילי), StatefulSet, ו-HPA

## איך השיעור עובד

בשיעור: הרצאה והדגמות. אתן עוקבות במדריך, ושואלות. את הכל מתרגלות בבית.

## תרגולים לבית

[exercises.md](exercises.md): שישה תרגולים, לפי הסדר, עם פתרון מקופל מתחת לכל אחד. לא מוגש.

1. stats ו-frontend: אותה תבנית (10 דקות)
2. מחזור חיים שלם, על release שלישי (15 דקות)
3. requests ו-limits, ו-OOMKilled (15 דקות)
4. גיבוי לילי: CronJob (20 דקות)
5. בונוס: HPA (20 דקות)
6. StatefulSet: שאלות על הנייר (10 דקות)

## שיעורי בית

[homework.md](homework.md): **מסמך דרישות.** לבנות בבית את ה-chart של ShopList, להתקין אותו, לעדכן, לשבור ולחזור אחורה, ולהוסיף resources וגיבוי. הגשה ב-push מהבית, לפני שיעור 8.

## הקבצים בתיקייה

| קובץ | מה יש בו |
|---|---|
| [guide.md](guide.md) | מדריך: מושגים, וכל ה-chart שלב אחר שלב |
| [exercises.md](exercises.md) | תרגולים לבית, עם פתרונות |
| [homework.md](homework.md) | **שיעורי בית** |

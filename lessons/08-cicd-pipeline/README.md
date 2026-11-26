# שיעור 8: CI/CD — הרובוט שבונה בשבילנו

## מה לומדות בשיעור

- למה CI/CD: שבעה צעדים ידניים בכל שינוי, ומה משתבש בהם
- CI, Continuous Delivery ו-Continuous Deployment, ומה זה pipeline
- GitHub Actions: workflow, event, job, step, runner, ו-`uses` מול `run`
- בקרת איכות: job של בדיקות שעוצר הכל כשמשהו שבור
- registry: `ghcr.io`, שם של image, ולמה תגית של commit עדיפה על `latest`
- `GITHUB_TOKEN`, `permissions` ו-Secrets: איך pipeline מתחבר, בלי סיסמה בקוד
- `matrix` ו-`needs`: שלושה images במקביל, רק אחרי שהבדיקות עברו
- מהמחסן אל ה-cluster: `values-registry.yaml` ו-`helm upgrade` עם התגית מה-pipeline

## איך השיעור עובד

בשיעור: הרצאה והדגמות על הריפו שלי. אתן עוקבות במדריך, ושואלות. את הכל מתרגלות בבית.

## תרגולים לבית

הקובץ [exercises.md](exercises.md): שישה תרגולים, לפי הסדר, עם פתרון מקופל מתחת לכל אחד. לא מוגש.

1. לקרוא workflow, על הנייר (10 דקות)
2. hello, ומה הסדר עושה (15 דקות)
3. מצאו את הטעות (15 דקות)
4. בקרת איכות שעובדת (20 דקות)
5. matrix ו-needs (20 דקות)
6. מהמחסן אל ה-cluster (20 דקות)

## שיעורי בית

הקובץ [homework.md](homework.md): **מסמך דרישות.** לבנות pipeline שבודק, בונה ומעלה את שלושת ה-images ל-`ghcr.io`, ולהתקין ב-cluster את מה שהוא בנה. הגשה ב-push מהבית, לפני שיעור 9.

## הקבצים בתיקייה

| קובץ | מה יש בו |
|---|---|
| [guide.md](guide.md) | מדריך: מושגים, וכל ה-workflow שלב אחר שלב |
| [exercises.md](exercises.md) | תרגולים לבית, עם פתרונות |
| [homework.md](homework.md) | **שיעורי בית** |

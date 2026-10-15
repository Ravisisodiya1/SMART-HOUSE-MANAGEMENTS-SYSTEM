# API (all under /api/, JWT `Authorization: Bearer <access>`)
POST auth/register/ · auth/login/ ({username: email, password}) · auth/refresh/ · auth/logout/ · GET/PATCH auth/profile/ · POST auth/change-password/
GET/POST/PUT house/ · GET dashboard/ · GET ai/insights/ · POST ai/chat/ ({message}) · GET reports/?type=expenses|income|bills&format=csv&date_from=&date_to=
CRUD (list supports ?search=, ?ordering=, ?page=, exact filters like ?category=Food, ?date_from=&date_to=):
expenses/ income/ budgets/ bills/ tasks/ shopping/ maintenance/ assets/ documents/ family/
notifications/ (GET, PATCH is_read, DELETE)

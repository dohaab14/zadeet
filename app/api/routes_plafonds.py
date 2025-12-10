




@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    recent = services_transactions.get_recent_transactions(db, limit=3)
    categories = services_categories.get_categories(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "recent_transactions": recent,
        "categories": categories
    })


@app.get("/api/dashboard-charts")
def get_charts_data(db: Session = Depends(get_db)):
    bar_data = services_accueil.get_last_3_months_stats(db)
    pie_data = services_accueil.get_category_pie_stats(db)
    return {
        "bar_chart": bar_data,
        "pie_chart": pie_data
    }


@app.get("/api/total-balance")
def get_total_balance(db: Session = Depends(get_db)):
    total_balance = services_accueil.get_total_balance(db)
    return {
        "total_balance": total_balance or 0.0
    }


@app.get("/api/recent-transactions")
def get_recent_transactions_api(db: Session = Depends(get_db)):
    recent_transactions = services_transactions.get_recent_transactions(db)
    return recent_transactions

use crate::infrastructure::surrealdb::DbConfig;
use crate::models::user_repository::{UserRepository, UserRepositorySurreal};
use crate::presentation::routes::user_routes;
use crate::services::user_service::UserService;
use actix_web::middleware::Logger;
use actix_web::{App, HttpServer, web};
use std::sync::LazyLock;
use surrealdb::Surreal;
use surrealdb::engine::remote::ws::Client;

static DB: LazyLock<Surreal<Client>> = LazyLock::new(Surreal::init);

mod domain;
mod infrastructure;
mod models;
mod presentation;
mod services;

mod error {
    use actix_web::{HttpResponse, ResponseError};
    use thiserror::Error;

    #[derive(Error, Debug)]
    pub enum Error {
        #[error("database error")]
        Db(String),
    }

    impl ResponseError for Error {
        fn error_response(&self) -> HttpResponse {
            match self {
                Error::Db(e) => HttpResponse::InternalServerError().body(e.to_string()),
            }
        }
    }

    impl From<surrealdb::Error> for Error {
        fn from(error: surrealdb::Error) -> Self {
            eprintln!("{error}");
            Self::Db(error.to_string())
        }
    }
}

#[actix_web::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let db_config = DbConfig {
        host: String::from("localhost"),
        port: 8000u16,
        username: String::from("root"),
        password: String::from("root"),
        namespace: String::from("application"),
        database: String::from("users"),
    };

    let user_repository = UserRepositorySurreal::new(db_config).await;
    let user_service = UserService::new(user_repository);

    let app_data_service = web::Data::new(user_service);

    HttpServer::new(move || {
        App::new()
            .app_data(app_data_service.clone())
            .wrap(Logger::default())
            .configure(user_routes::routes)
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await;

    Ok(())
}

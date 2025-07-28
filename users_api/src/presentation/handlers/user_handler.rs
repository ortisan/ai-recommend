use crate::domain::user_domain::UserDomain;
use crate::models::user_repository::UserRepositorySurreal;
use crate::services::user_service::UserService;
use actix_web::{HttpResponse, get, post, web, delete};
use uuid::Uuid;

#[post("/")]
pub async fn create_user(
    user_service: web::Data<UserService<UserRepositorySurreal>>,
    user_data: web::Json<UserDomain>,
) -> HttpResponse {
    let mut user_domain = user_data.into_inner();
    let id = Uuid::now_v7().to_string();
    user_domain.id = Some(id);

    let created_user_result = user_service.create_user(user_domain).await;
    match created_user_result {
        Ok(created_user_domain) => HttpResponse::Created().json(created_user_domain),
        Err(error) => HttpResponse::InternalServerError().json(error),
    }
}

#[get("/{user_id}/")]
pub async fn get_user_by_id(
    user_service: web::Data<UserService<UserRepositorySurreal>>,
    user_id: web::Path<String>,
) -> HttpResponse {
    let get_user_result = user_service.get_user_by_id(user_id.into_inner()).await;
    match get_user_result {
        Ok(user_domain) => HttpResponse::Ok().json(user_domain),
        Err(error) => HttpResponse::InternalServerError().json(error),
    }
}

#[delete("/{user_id}/")]
pub async fn delete_user_by_id(
    user_service: web::Data<UserService<UserRepositorySurreal>>,
    user_id: web::Path<String>,
) -> HttpResponse {
    let delete_result = user_service.delete_user_by_id(user_id.into_inner()).await;
    match delete_result {
        Ok(user_domain) => HttpResponse::Ok().finish(),
        Err(error) => HttpResponse::InternalServerError().json(error),
    }
}

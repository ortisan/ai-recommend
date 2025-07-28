use crate::presentation::handlers::user_handler::{create_user, delete_user_by_id, get_user_by_id};
use actix_web::web;

pub fn routes(config: &mut web::ServiceConfig) {
    config.service(web::scope("/users")
        .service(create_user)
        .service(get_user_by_id)
        .service(delete_user_by_id)
    );
}

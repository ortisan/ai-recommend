use crate::presentation::handlers::user_handler::{create_user, get_user};
use actix_web::web;

pub fn routes(config: &mut web::ServiceConfig) {
    config.service(web::scope("/users").service(create_user).service(get_user));
}

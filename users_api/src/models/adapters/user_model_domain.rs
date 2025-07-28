use crate::domain::user_domain::UserDomain;
pub use crate::models::user_model::UserModel;
use crate::models::user_repository::USERS_TABLE;
use regex::Regex;
use std::str::FromStr;
use surrealdb::RecordId;

impl From<UserDomain> for UserModel {
    fn from(source: UserDomain) -> Self {
        let id_str = format!("{}:`{}`", USERS_TABLE, source.id.unwrap());
        let id = RecordId::from_str(&id_str).unwrap();
        UserModel {
            name: source.name,
            email: source.email,
            username: source.username,
            password: source.password,
            created_at: String::from("2025-07-26"),
            updated_at: String::from("2025-07-26"),
            id,
        }
    }
}
impl From<UserModel> for UserDomain {
    fn from(source: UserModel) -> Self {
        let re = Regex::new(r"[⟨⟩]").unwrap();
        let id_str = source.id.key().to_string();
        let id = re.replace_all(&id_str, "");
        UserDomain {
            id: Some(id.to_string()),
            name: source.name,
            email: source.email,
            username: source.username,
            password: source.password,
        }
    }
}

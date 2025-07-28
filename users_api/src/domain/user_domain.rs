use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct UserDomain {
    pub id: Option<String>,
    pub name: String,
    pub email: String,
    pub username: String,
    pub password: String,
}
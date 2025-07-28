use serde::{Deserialize, Serialize};
use surrealdb::RecordId;

#[derive(Serialize, Deserialize)]
pub struct UserModel {
    pub id: RecordId,
    pub name: String,
    pub email: String,
    pub username: String,
    pub password: String,
    pub created_at: String,
    pub updated_at: String,
}


use crate::infrastructure::surrealdb::{DbConfig, get_database};
use crate::models::user_model::UserModel;
use surrealdb::engine::remote::ws::Client;
use surrealdb::error::Db::Thrown;
use surrealdb::{Error, Surreal};

pub const USERS_TABLE: &str = "users";

pub struct UserRepositorySurreal {
    table: String,
    db: Surreal<Client>,
}

impl UserRepositorySurreal {
    pub async fn new(config: DbConfig) -> Self {
        let db = get_database(config).await.unwrap();
        UserRepositorySurreal {
            table: String::from(USERS_TABLE),
            db,
        }
    }
}

pub trait UserRepository {
    async fn create(&self, model: UserModel) -> Result<UserModel, Error>;
    async fn get_by_id(&self, id: String) -> Result<UserModel, Error>;
}

impl UserRepository for UserRepositorySurreal {
    async fn create(&self, model: UserModel) -> Result<UserModel, Error> {
        let creation_result: Result<Option<UserModel>, Error> =
            self.db.create(&self.table).content(model).await;
        match creation_result {
            Ok(Some(record)) => Ok(record),
            Ok(None) => Err(Error::Db(Thrown(String::from("User creation failed")))),
            Err(error) => Err(error),
        }
    }

    async fn get_by_id(&self, id: String) -> Result<UserModel, Error> {
        if let Some(record) = self.db.select((&self.table, id.clone())).await? {
            return Ok(record);
        }
        let error = Error::Db(Thrown(format!("User with id {} not found", id)));
        Err(error)
    }
}

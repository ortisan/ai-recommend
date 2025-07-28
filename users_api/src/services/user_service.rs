use surrealdb::Error;
use crate::domain::user_domain::UserDomain;
use crate::models::user_model::UserModel;
use crate::models::user_repository::{UserRepository};

#[derive(Clone)]
pub struct UserService<T: UserRepository> {
    user_repository: T,
}

impl <T: UserRepository> UserService<T> {
    pub fn new(user_repository: T) -> Self {
        UserService {
            user_repository
        }
    }

    pub async fn create_user(&self, user_domain: UserDomain) -> Result<UserDomain, Error> {
        let create_result = self.user_repository.create(UserModel::from(user_domain)).await;
        match create_result {
            Ok(model) => Ok(UserDomain::from(model)),
            Err(e) => Err(e)
        }
    }

    pub async fn get_user_by_id(&self, user_id: String) -> Result<UserDomain, Error> {
        let get_by_id_result = self.user_repository.get_by_id(user_id).await?;
        Ok(UserDomain::from(get_by_id_result))
    }

    pub async fn delete_user_by_id(&self, user_id: String) -> Result<(), Error> {
        let delete_result = self.user_repository.delete_by_id(user_id).await?;
        Ok(delete_result)
    }
}
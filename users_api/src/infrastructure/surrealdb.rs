use surrealdb::engine::remote::ws::{Client, Ws};
use surrealdb::opt::auth::Root;
use surrealdb::{Result, Surreal};

pub struct DbConfig {
    pub host: String,
    pub port: u16,
    pub username: String,
    pub password: String,
    pub namespace: String,
    pub database: String,
}

impl DbConfig {
    fn get_address(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }
}

pub async fn get_database(config: DbConfig) -> Result<Surreal<Client>> {
    let db: Surreal<Client> = Surreal::init();
    let _ = db.connect::<Ws>(config.get_address()).await?;
    let _ = db.signin(Root {
        username: &config.username,
        password: &config.password,
    })
    .await?;
    let _ = db.use_ns(config.namespace).use_db(config.database).await?;
    Ok(db)
}

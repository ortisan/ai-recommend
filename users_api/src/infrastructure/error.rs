use std::fmt::Display;

pub struct ErrorData {
    code: String,
    message: String,
    args: Vec<String>,
}

pub enum GenericError {

}
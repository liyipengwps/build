/*
 * Copyright (c) 2023 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

//! autocxx demo when rust call cpp
use autocxx::prelude::*;
include_cpp! {
    #include "build/rust/tests/test_autocxx/tests/autocxx_rust_call_cpp/src/Dog.h"
    safety!(unsafe_ffi)
    generate!("DoMath")
    generate!("Dog")
}

/// pub fn autocxx_rust_call_cpp()
pub fn autocxx_rust_call_cpp() {
  println!("Hello, world! - C++ math should say 12={}", ffi::DoMath(4));
}


/// autocxx main for autocxx_rust_call_cpp
fn main() {
    autocxx_rust_call_cpp();
}

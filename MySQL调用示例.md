# MCP MySQL工具调用示例

## 1. create_mysql_connection - 创建MySQL数据库连接

### 连接到您的本地MySQL（推荐使用）
```python
await client.call_tool(
    tool_name="create_mysql_connection",
    arguments={
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "Ll@2120516678",
        "database": "test_db",
        "charset": "utf8mb4"
    }
)
```

### 仅连接到MySQL服务器（不指定数据库）
```python
await client.call_tool(
    tool_name="create_mysql_connection",
    arguments={
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "Ll@2120516678"
    }
)
```

### 连接到其他数据库
```python
await client.call_tool(
    tool_name="create_mysql_connection",
    arguments={
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "Ll@2120516678",
        "database": "my_project_db",
        "charset": "utf8mb4"
    }
)
```

## 2. get_connection_status - 获取连接状态

```python
await client.call_tool(
    tool_name="get_connection_status",
    arguments={}
)
```

## 3. create_database - 创建数据库

### 创建基本数据库
```python
await client.call_tool(
    tool_name="create_database",
    arguments={
        "database_name": "my_new_database",
        "charset": "utf8mb4"
    }
)
```

### 创建指定字符集的数据库
```python
await client.call_tool(
    tool_name="create_database",
    arguments={
        "database_name": "blog_system",
        "charset": "utf8"
    }
)
```

## 4. use_database - 切换数据库

```python
await client.call_tool(
    tool_name="use_database",
    arguments={
        "database_name": "blog_system"
    }
)
```

## 5. execute_query - 执行查询语句

### 查询所有数据
```python
await client.call_tool(
    tool_name="execute_query",
    arguments={
        "sql": "SELECT * FROM users"
    }
)
```

### 带条件的查询
```python
await client.call_tool(
    tool_name="execute_query",
    arguments={
        "sql": "SELECT name, email, age FROM users WHERE age > 18 ORDER BY name"
    }
)
```

### 联表查询
```python
await client.call_tool(
    tool_name="execute_query",
    arguments={
        "sql": "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id WHERE u.status = 'active'"
    }
)
```

### 统计查询
```python
await client.call_tool(
    tool_name="execute_query",
    arguments={
        "sql": "SELECT COUNT(*) as total_users, AVG(age) as avg_age FROM users"
    }
)
```

## 6. execute_update - 执行修改语句

### INSERT语句
```python
await client.call_tool(
    tool_name="execute_update",
    arguments={
        "sql": "INSERT INTO users (name, email, age) VALUES ('张三', 'zhangsan@example.com', 25)"
    }
)
```

### UPDATE语句
```python
await client.call_tool(
    tool_name="execute_update",
    arguments={
        "sql": "UPDATE users SET age = 26, email = 'zhangsan_new@example.com' WHERE name = '张三'"
    }
)
```

### DELETE语句
```python
await client.call_tool(
    tool_name="execute_update",
    arguments={
        "sql": "DELETE FROM users WHERE age < 18"
    }
)
```

### 批量插入
```python
await client.call_tool(
    tool_name="execute_update",
    arguments={
        "sql": "INSERT INTO products (name, price, category) VALUES ('iPhone 15', 999.99, 'electronics'), ('MacBook Pro', 2499.99, 'electronics')"
    }
)
```

## 7. show_tables - 显示所有表

```python
await client.call_tool(
    tool_name="show_tables",
    arguments={}
)
```

## 8. describe_table - 查看表结构

### 查看用户表结构
```python
await client.call_tool(
    tool_name="describe_table",
    arguments={
        "table_name": "users"
    }
)
```

### 查看订单表结构
```python
await client.call_tool(
    tool_name="describe_table",
    arguments={
        "table_name": "orders"
    }
)
```

## 9. show_databases - 显示所有数据库

```python
await client.call_tool(
    tool_name="show_databases",
    arguments={}
)
```

## 10. create_table - 创建表

### 创建用户表
```python
await client.call_tool(
    tool_name="create_table",
    arguments={
        "table_name": "users",
        "columns_definition": "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(150) UNIQUE, age INT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
)
```

### 创建产品表
```python
await client.call_tool(
    tool_name="create_table",
    arguments={
        "table_name": "products",
        "columns_definition": "product_id INT PRIMARY KEY, product_name VARCHAR(255) NOT NULL, price DECIMAL(10,2), category VARCHAR(50), stock_quantity INT DEFAULT 0"
    }
)
```

### 创建订单表
```python
await client.call_tool(
    tool_name="create_table",
    arguments={
        "table_name": "orders",
        "columns_definition": "order_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, product_id INT, quantity INT, total_amount DECIMAL(10,2), order_date DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (product_id) REFERENCES products(product_id)"
    }
)
```

## 11. drop_table - 删除表

### 删除临时表
```python
await client.call_tool(
    tool_name="drop_table",
    arguments={
        "table_name": "temp_data"
    }
)
```

### 删除旧的日志表
```python
await client.call_tool(
    tool_name="drop_table",
    arguments={
        "table_name": "old_logs"
    }
)
```

## 12. insert_data - 插入数据

### 插入单个用户
```python
await client.call_tool(
    tool_name="insert_data",
    arguments={
        "table_name": "users",
        "columns": "name, email, age",
        "values": "'李四', 'lisi@example.com', 28"
    }
)
```

### 插入产品信息
```python
await client.call_tool(
    tool_name="insert_data",
    arguments={
        "table_name": "products",
        "columns": "product_name, price, category, stock_quantity",
        "values": "'MacBook Air', 1299.99, 'electronics', 50"
    }
)
```

### 插入订单信息
```python
await client.call_tool(
    tool_name="insert_data",
    arguments={
        "table_name": "orders",
        "columns": "user_id, product_id, quantity, total_amount",
        "values": "1, 100, 2, 599.98"
    }
)
```

## 13. update_data - 更新数据

### 更新用户信息
```python
await client.call_tool(
    tool_name="update_data",
    arguments={
        "table_name": "users",
        "set_clause": "name='王五', age=30",
        "where_clause": "id=1"
    }
)
```

### 更新产品价格
```python
await client.call_tool(
    tool_name="update_data",
    arguments={
        "table_name": "products",
        "set_clause": "price=899.99, stock_quantity=25",
        "where_clause": "product_name='iPhone 15'"
    }
)
```

### 批量更新订单状态
```python
await client.call_tool(
    tool_name="update_data",
    arguments={
        "table_name": "orders",
        "set_clause": "status='shipped'",
        "where_clause": "order_date < '2024-01-01' AND status='pending'"
    }
)
```

## 14. delete_data - 删除数据

### 删除特定用户
```python
await client.call_tool(
    tool_name="delete_data",
    arguments={
        "table_name": "users",
        "where_clause": "id=5"
    }
)
```

### 删除过期订单
```python
await client.call_tool(
    tool_name="delete_data",
    arguments={
        "table_name": "orders",
        "where_clause": "order_date < '2023-01-01' AND status='cancelled'"
    }
)
```

### 清空整个表（谨慎使用）
```python
await client.call_tool(
    tool_name="delete_data",
    arguments={
        "table_name": "temp_logs",
        "where_clause": "1=1"
    }
)
```

## 15. close_connection - 关闭连接

```python
await client.call_tool(
    tool_name="close_connection",
    arguments={}
)
```

## 完整使用流程示例（使用您的本地MySQL）

```python
# 1. 建立连接到您的本地MySQL
await client.call_tool(
    tool_name="create_mysql_connection",
    arguments={
        "host": "localhost",
        "user": "root",
        "password": "Ll@2120516678",
        "database": "test_db"
    }
)

# 2. 检查连接状态
await client.call_tool(
    tool_name="get_connection_status",
    arguments={}
)

# 3. 创建表
await client.call_tool(
    tool_name="create_table",
    arguments={
        "table_name": "employees",
        "columns_definition": "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), department VARCHAR(50), salary DECIMAL(10,2)"
    }
)

# 4. 插入数据
await client.call_tool(
    tool_name="insert_data",
    arguments={
        "table_name": "employees",
        "columns": "name, department, salary",
        "values": "'张三', '技术部', 8000.00"
    }
)

# 5. 查询数据
await client.call_tool(
    tool_name="execute_query",
    arguments={
        "sql": "SELECT * FROM employees WHERE department = '技术部'"
    }
)

# 6. 关闭连接
await client.call_tool(
    tool_name="close_connection",
    arguments={}
)
```

## 快速开始示例（适合您的环境）

```python
# 快速连接并开始使用
await client.call_tool(
    tool_name="create_mysql_connection",
    arguments={
        "host": "localhost",
        "user": "root",
        "password": "Ll@2120516678"
    }
)

# 查看现有数据库
await client.call_tool(
    tool_name="show_databases",
    arguments={}
)

# 创建新的测试数据库
await client.call_tool(
    tool_name="create_database",
    arguments={
        "database_name": "my_test_db"
    }
)

# 切换到新数据库
await client.call_tool(
    tool_name="use_database",
    arguments={
        "database_name": "my_test_db"
    }
)
```

## 注意事项

1. **连接管理**: 使用前必須先调用 `create_mysql_connection` 建立连接
2. **字符串值**: 在SQL语句中，字符串值必须用单引号包围
3. **安全性**: 删除操作必须提供WHERE条件，避免误删所有数据
4. **错误处理**: 所有工具都会返回success字段，请检查执行结果
5. **资源释放**: 使用完毕后建议调用 `close_connection` 关闭连接
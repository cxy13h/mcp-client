# MCP-Client

这是一个使用 **UV** 进行环境管理的项目。

## 环境设置 (Environment Setup)

请按照以下步骤设置并运行项目：

### 1\. 安装 UV

本项目使用 [UV](https://github.com/astral-sh/uv) 作为环境管理工具。请根据您的操作系统，**自行安装 UV**。您可以参考 UV 的官方文档获取详细的安装指南。

### 2\. 构建虚拟环境 (Building the Virtual Environment)

安装 UV 后，请导航到本项目的根目录。然后运行以下命令来构建项目的虚拟环境并安装所需的依赖：

```
uv sync
```

这个命令会创建一个 `.venv` 虚拟环境，并安装 `pyproject.toml` 中指定的所有依赖项。

### 3\. 运行项目 (Running the Project)

虚拟环境构建完成后，您可以使用 UV 来运行 `main.py` 文件：

```
uv run main.py
```

## MCP Server 提供的工具 (Tools Provided by MCP Server)

MCP Server 提供了以下工具，您可以在项目中根据需要使用它们：

### 工具列表 (Tool List)

#### `all_table_names`

  * **描述 (Description):** 返回数据库中所有表名，以','分隔。已连接到 mysql version 8.0.42.24.4.1 database testdb on localhost as user root.
  * **输入参数 (Input Schema):** 无 (No required arguments)

#### `filter_table_names`

  * **描述 (Description):** 返回数据库中包含子字符串'q'的所有表名，以逗号分隔。已连接到 mysql version 8.0.42.24.4.1 database testdb on localhost as user root.
  * **输入参数 (Input Schema):**
      * `q` (字符串): 用于过滤表名的子字符串 (Substring to filter table names)
      * **必填 (Required):** 是 (Yes)

#### `schema_definitions`

  * **描述 (Description):** 返回给定表的模式和关系信息。已连接到 mysql version 8.0.42.24.4.1 database testdb on localhost as user root.
  * **输入参数 (Input Schema):**
      * `table_names` (数组): 要查询结构信息的表名列表 (List of table names to query schema information)
      * **必填 (Required):** 是 (Yes)

#### `execute_query`

  * **描述 (Description):** 执行SQL查询并以可读格式返回结果。结果将在4000字符后截断。 重要提示：始终使用params参数进行查询参数替换（例如'WHERE id = :id'配合params={'id': 123}）以防止SQL注入。直接字符串拼接是严重的安全风险。 已连接到 mysql version 8.0.42.24.4.1 database testdb on localhost as user root.
  * **输入参数 (Input Schema):**
      * `query` (字符串): 要执行的SQL查询语句 (SQL query statement to execute)
      * **必填 (Required):** 是 (Yes)
      * `params` (对象): 查询参数字典，用于安全的参数替换，防止SQL注入 (Dictionary of query parameters for safe parameter substitution, preventing SQL injection)
      * **必填 (Required):** 否 (No)
      * **默认值 (Default Value):** `{}`

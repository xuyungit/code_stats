# API Enhancement Discussion - Cross-Repo Statistics

## Date: 2025-01-06

## Discussion Summary

### Core Requirements Identified

用户提出了对现有统计系统的增强需求：

1. **统计指标确认**
   - Commits: 提交数量
   - Added Lines: 新增代码行数  
   - Deleted Lines: 删除代码行数
   - Files Changed: 变更文件数
   - Net Change: 净变化 (added - deleted)
   - Code Activities: 代码活动量 (added + deleted) - 体现总体工作量，包括重构删除的贡献

2. **数据存储和计算策略**
   - **原始需求**: 预计算所有统计结果存储在数据库中
   - **最终决定**: 保持现有设计 - 只存储原子数据，运行时计算派生指标
   - **理由**: net_change 和 code_activities 是简单加减法，避免数据冗余

3. **跨仓库统计需求**
   - 需要支持用户所有仓库的汇总统计
   - 按作者汇总每日贡献（跨多个仓库）
   - 支持按作者过滤（包括AI编码者过滤）
   - 支持7日/14日等周期汇总

### API设计演进

#### 初始设计 (过度设计)
考虑了复杂的统一API设计，包含灵活的group_by参数和复杂的响应结构。

#### 最终设计 (实用导向)
**API端点**: `GET /api/stats/repo-daily`

**查询参数**:
- `date_from`: 开始日期 (必填)
- `date_to`: 结束日期 (必填)  
- `repo`: 仓库ID或"all" (必填)
- `exclude_ai`: 排除AI编码者 (可选)

**响应结构**:
```json
{
  "daily_stats": [
    {
      "date": "2024-01-01",
      "daily_stats": [
        {
          "author_id": 1,
          "commits_count": 3,
          "added_lines": 120,
          "deleted_lines": 45,
          "files_changed": 8
        }
      ]
    }
  ],
  "date_range": "2024-01-01 to 2024-01-07",
  "repositories_included": [1, 2, 3]
}
```

### 设计优势

1. **以日期为主索引**: 方便前端展示时间线图表
2. **数据最小化**: 只返回author_id，避免重复的author信息
3. **解耦设计**: 前端可通过author API单独获取作者详情
4. **统一接口**: 单仓库和跨仓库使用同一API
5. **前端灵活性**: 汇总计算由前端处理，支持各种展示需求

### 实现的Schema

#### 新增Schema类
- `AuthorDailyContribution`: 单个作者的日贡献数据
- `DailyStatsWithAuthors`: 包含日期和该日所有作者贡献的容器
- `RepoDailyResponse`: 完整的API响应结构

#### 服务层实现
- `StatisticsService.get_repo_daily_stats()`: 核心业务逻辑
- 支持用户权限验证
- 支持AI编码者过滤
- 支持单仓库和跨仓库查询

### 关键决策点

1. **避免过度设计**: 从复杂的统一API回归到简单实用的设计
2. **数据库策略**: 保持原子数据存储，避免冗余计算字段
3. **前端职责**: 将汇总计算和数据组装的职责交给前端
4. **API简洁性**: 参数简单明确，响应结构清晰

### 使用示例

```bash
# 查看所有仓库7天统计
GET /api/stats/repo-daily?date_from=2024-01-01&date_to=2024-01-07&repo=all

# 查看特定仓库统计  
GET /api/stats/repo-daily?date_from=2024-01-01&date_to=2024-01-07&repo=123

# 排除AI编码者
GET /api/stats/repo-daily?date_from=2024-01-01&date_to=2024-01-07&repo=all&exclude_ai=true
```

## 技术实现

### 文件变更
- `backend/app/schemas/statistics.py`: 新增响应schema
- `backend/app/statistics/services.py`: 新增跨仓库查询服务
- `backend/app/statistics/routes.py`: 新增API路由
- `backend/app/main.py`: 注册新路由

### 数据库查询优化
- 使用JOIN查询提高效率
- 支持日期范围过滤
- 支持用户权限过滤
- 支持AI编码者过滤

## 下一步计划

1. **前端实现**: 基于新API实现跨仓库统计页面
2. **性能优化**: 针对大数据量的查询优化
3. **缓存策略**: 考虑对频繁查询的统计数据进行缓存
4. **更多过滤选项**: 可能增加时间粒度、作者组等更多过滤维度
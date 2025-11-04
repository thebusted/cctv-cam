# CLAUDE.md Templates

Ready-to-use templates for different project types. Copy the appropriate template and customize for your specific project.

## Full-Stack Web Application (React + Node.js)

```markdown
# Project: [Project Name] - [Brief description]

## Architecture
- Frontend: React 18 with TypeScript
- State management: Redux Toolkit with RTK Query
- Backend: Node.js + Express.js
- Database: PostgreSQL with Prisma ORM
- Authentication: JWT with refresh tokens
- Testing: Jest + React Testing Library + Supertest

## Development Commands
- `npm run dev`: Start both frontend (3000) and backend (5000)
- `npm run dev:frontend`: Start only frontend
- `npm run dev:backend`: Start only backend
- `npm run test`: Run all tests
- `npm run test:watch`: Run tests in watch mode
- `npm run build`: Build for production
- `npm run lint`: Run ESLint
- `npm run migrate`: Run database migrations
- `npm run seed`: Seed database with test data

## Code Style Guidelines
- TypeScript for all new files (strict mode enabled)
- Functional React components with hooks
- Async/await over Promise chains
- Named exports for components
- Default exports for pages
- CSS modules for styling (*.module.css)
- API responses follow { data, error } pattern

## Project Structure
- `/frontend`: React application
  - `/src/components`: Reusable components
  - `/src/pages`: Route components
  - `/src/services`: API client code
  - `/src/store`: Redux store and slices
- `/backend`: Express server
  - `/src/routes`: API endpoints
  - `/src/controllers`: Request handlers
  - `/src/models`: Database models
  - `/src/middleware`: Express middleware
- `/shared`: Shared types and utilities

## Testing Conventions
- Unit tests: *.test.ts alongside source files
- Integration tests: /tests/integration/
- E2E tests: /tests/e2e/ using Playwright
- Test database: Use .env.test configuration
- Coverage target: 80% for critical paths

## Workflow Rules
- Branch from develop, not main
- Branch naming: feature/JIRA-123-description
- Commit format: "type(scope): message"
- PR requires: passing tests, code review, updated docs
- Squash merge into develop
- Release branches for production

## API Conventions
- RESTful endpoints: GET /api/v1/resources
- Pagination: ?page=1&limit=20&sort=-createdAt
- Filtering: ?filter[status]=active
- Error responses: { error: { code, message, details } }
- Always validate with Zod schemas

## Security Patterns
- Input validation on all endpoints
- Rate limiting: 100 req/min per IP
- CORS configured for specific origins
- Helmet.js for security headers
- bcrypt for password hashing (rounds: 10)
- JWT in httpOnly cookies

## Performance Guidelines
- Bundle size: <250KB gzipped
- Lazy load routes with React.lazy()
- Image optimization with next/image
- API response time: p95 <500ms
- Database queries: Use indexes, avoid N+1
- Cache with Redis for frequent queries

## Environment Variables
- Copy .env.example to .env
- Never commit .env files
- Required vars documented in .env.example
- Use process.env.NODE_ENV checks
- Validate env vars on startup

## Deployment
- Staging: Automatically deploys from develop
- Production: Manual deploy from main
- Run migrations before deploying new code
- Health check endpoint: /api/health
- Rollback plan documented in DEPLOYMENT.md
```

## Backend API Service

```markdown
# Project: [API Name] - RESTful API Service

## Architecture
- Framework: Express.js with TypeScript
- Database: PostgreSQL with Knex.js
- Queue: Bull with Redis
- Logging: Winston with correlation IDs
- Monitoring: Prometheus metrics
- Documentation: OpenAPI 3.0

## Development Commands
- `npm run dev`: Start with hot reload (port 3000)
- `npm run test`: Run test suite
- `npm run test:integration`: Run integration tests
- `npm run migrate:latest`: Run migrations
- `npm run migrate:rollback`: Rollback last migration
- `npm run seed`: Seed development data
- `npm run docs`: Generate API documentation

## Code Organization
- `/src/controllers`: Request handling logic
- `/src/services`: Business logic
- `/src/models`: Database models
- `/src/middleware`: Express middleware
- `/src/validators`: Request validation schemas
- `/src/utils`: Shared utilities
- `/src/jobs`: Background job processors

## API Design Patterns
- Version in URL: /api/v1/
- Resource naming: Plural nouns
- HTTP methods: GET, POST, PUT, PATCH, DELETE
- Status codes: Follow RFC standards
- Pagination: Cursor-based for large datasets
- Sorting: ?sort=field1,-field2
- Filtering: ?filter[field]=value

## Database Conventions
- Migrations: Always forward-compatible
- Naming: snake_case for tables/columns
- Timestamps: created_at, updated_at on all tables
- Soft deletes: deleted_at for recoverable data
- Foreign keys: table_id pattern
- Indexes: Add for all foreign keys and frequent queries

## Testing Strategy
- Unit tests: Mock external dependencies
- Integration tests: Use test database
- Contract tests: Validate API contracts
- Load tests: Run before major releases
- Test data: Factories over fixtures

## Error Handling
- Custom error classes for different types
- Consistent error response format
- Log errors with context
- Don't expose internal details
- Rate limit error responses
- Circuit breakers for external services

## Security Requirements
- Authenticate all endpoints (except public)
- Authorize based on user roles
- Validate all inputs with Joi/Zod
- Sanitize data before storage
- Use parameterized queries
- Implement rate limiting
- Add request ID tracking

## Performance Optimization
- Database query optimization
- Implement caching strategy
- Use database connection pooling
- Compress responses with gzip
- Implement pagination on all lists
- Profile and optimize slow queries

## Monitoring & Logging
- Log levels: ERROR, WARN, INFO, DEBUG
- Structured logging (JSON format)
- Correlation IDs for request tracking
- Metrics: Response time, error rate, throughput
- Alerts: Set up for critical errors
- Health checks: Database, Redis, external services
```

## Data Science / ML Project

```markdown
# Project: [Project Name] - ML Pipeline

## Architecture
- Language: Python 3.11
- ML Framework: PyTorch 2.0 / scikit-learn
- Data Processing: Pandas, Polars
- Experiment Tracking: MLflow
- Model Registry: MLflow Model Registry
- Orchestration: Airflow
- Infrastructure: Docker + Kubernetes

## Development Commands
- `make setup`: Install dependencies and pre-commit hooks
- `make train`: Train model with default config
- `make evaluate`: Run model evaluation
- `make serve`: Start model serving API
- `make test`: Run test suite
- `make lint`: Run linting (black, flake8, mypy)
- `make notebook`: Start Jupyter server

## Project Structure
- `/data`: Data storage (not in git)
  - `/raw`: Original, immutable data
  - `/interim`: Intermediate transformed data
  - `/processed`: Final data for modeling
- `/models`: Trained model artifacts
- `/notebooks`: Jupyter notebooks for exploration
- `/src`: Source code
  - `/data`: Data loading and processing
  - `/features`: Feature engineering
  - `/models`: Model definitions and training
  - `/visualization`: Plotting utilities
- `/tests`: Test files

## Data Pipeline
1. Raw data ingestion from S3/database
2. Data validation with Great Expectations
3. Feature engineering pipeline
4. Train/validation/test split (60/20/20)
5. Model training with hyperparameter tuning
6. Model evaluation and comparison
7. Model registration if performance improves
8. Deployment to serving infrastructure

## Experiment Tracking
- Use MLflow for all experiments
- Tag experiments: purpose, dataset_version, author
- Log: Hyperparameters, metrics, artifacts
- Compare runs in MLflow UI
- Register best models to registry

## Model Development Guidelines
- Start with baseline model
- Use cross-validation for evaluation
- Document model assumptions
- Version datasets with DVC
- Reproducibility: Set random seeds
- Profile code for bottlenecks

## Testing Requirements
- Unit tests for data processing
- Integration tests for pipeline
- Model quality tests (no degradation)
- Data quality checks
- Performance benchmarks
- A/B testing for production models

## Code Quality Standards
- Type hints for all functions
- Docstrings (Google style)
- Max line length: 88 (black)
- Import order: isort
- Pre-commit hooks mandatory
- Code review before merging

## Deployment Process
- Models served via REST API
- Containerized with Docker
- Health checks required
- Model versioning strategy
- Rollback procedures documented
- Monitor model drift

## Performance Considerations
- Use vectorized operations
- Batch processing for inference
- GPU utilization monitoring
- Memory profiling for large datasets
- Optimize data loading pipeline
- Cache preprocessed features
```

## Mobile App (React Native)

```markdown
# Project: [App Name] - React Native Mobile App

## Architecture
- Framework: React Native 0.72 + Expo SDK 49
- Navigation: React Navigation 6
- State: Redux Toolkit + RTK Query
- UI Components: React Native Elements
- Forms: React Hook Form + Yup
- Testing: Jest + React Native Testing Library

## Development Commands
- `npm start`: Start Expo development server
- `npm run ios`: Run on iOS simulator
- `npm run android`: Run on Android emulator
- `npm run test`: Run test suite
- `npm run lint`: Run ESLint
- `npm run build:ios`: Build iOS app
- `npm run build:android`: Build Android app

## Project Structure
- `/src/screens`: Screen components
- `/src/components`: Reusable components
- `/src/navigation`: Navigation configuration
- `/src/services`: API and external services
- `/src/store`: Redux store configuration
- `/src/utils`: Helper functions
- `/src/constants`: App constants
- `/assets`: Images, fonts, etc.

## Development Guidelines
- TypeScript for all files
- Functional components only
- Custom hooks for logic reuse
- Memo components when needed
- Platform-specific code in *.ios.tsx / *.android.tsx

## Styling Patterns
- StyleSheet.create for performance
- Theme constants for colors/spacing
- Responsive design with Dimensions API
- Platform-specific styles when needed
- Avoid inline styles

## State Management
- Redux for global state
- Local state for UI-only state
- RTK Query for API caching
- Persist auth state with SecureStore
- Clear cache on logout

## API Integration
- Base URL from environment config
- Auth token in headers
- Refresh token flow implemented
- Offline queue for failed requests
- Error boundary for API errors

## Testing Approach
- Unit tests for utilities
- Component tests with RNTL
- Integration tests for flows
- Snapshot tests sparingly
- E2E with Detox for critical paths

## Performance Optimization
- FlatList for long lists
- Image caching with FastImage
- Lazy load screens
- Optimize re-renders with memo
- Monitor with Flipper

## Platform Considerations
- iOS: Handle notch, safe areas
- Android: Back button handling
- Permissions: Request when needed
- Deep linking configured
- Push notifications setup
```

## CLI Tool

```markdown
# Project: [Tool Name] - Command Line Tool

## Architecture
- Language: Node.js with TypeScript
- CLI Framework: Commander.js
- Configuration: Cosmiconfig
- Output: Chalk for colors, Ora for spinners
- Testing: Jest with snapshot tests

## Development Commands
- `npm run dev`: Run in development mode
- `npm run build`: Build for production
- `npm run test`: Run test suite
- `npm run test:watch`: Run tests in watch mode
- `npm link`: Link for local testing

## Project Structure
- `/src/commands`: Command implementations
- `/src/utils`: Shared utilities
- `/src/config`: Configuration handling
- `/src/templates`: File templates
- `/bin`: Entry point script

## CLI Design
- Subcommands: tool <command> [options]
- Global flags: --verbose, --quiet, --config
- Help text for all commands
- Version flag: --version
- Abbreviations for common flags

## Implementation Patterns
- Validate inputs early
- Provide helpful error messages
- Show progress for long operations
- Confirm destructive actions
- Support --dry-run flag
- Allow configuration files

## Error Handling
- Catch all errors at top level
- User-friendly error messages
- Exit codes: 0 success, 1 error
- Debug mode with --verbose
- Stack traces in development only

## Testing Strategy
- Unit tests for logic
- Integration tests for commands
- Snapshot tests for output
- Mock file system operations
- Test various input combinations

## Documentation
- README with examples
- Man page for Unix systems
- --help for every command
- Examples in help text
- Common use cases documented
```

## User-Level CLAUDE.md Template

```markdown
# User Preferences and Standards

## Personal Coding Style
- Prefer functional programming patterns
- Early returns over nested conditionals
- Descriptive variable names over comments
- Const by default, let when needed
- Prefer composition over inheritance

## Preferred Tools
- Editor: [Your editor]
- Terminal: [Your terminal]
- Git GUI: [If applicable]
- Package manager: [npm/yarn/pnpm]

## Common Workflows
- Always create feature branch from latest develop
- Run tests before committing
- Squash commits before merging
- Use conventional commits format

## Personal Shortcuts
- [Any personal command aliases]
- [Custom scripts you use]
- [Keyboard shortcuts to remember]

## Communication Preferences
- Prefer detailed error messages
- Include examples in documentation
- Explain "why" not just "what"
```

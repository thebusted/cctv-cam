# Real-World CLAUDE.md Examples

These are actual CLAUDE.md files from production projects that have proven effective. Names and some details have been anonymized.

## Example 1: E-commerce Platform

```markdown
# Project: ShopFlow - Multi-vendor E-commerce Platform

## Architecture
- Frontend: Next.js 14 with App Router
- State: Zustand for client, tRPC for server state
- Backend: Node.js with Fastify
- Database: PostgreSQL with Drizzle ORM
- Queue: BullMQ with Redis
- Payment: Stripe integration
- Search: Elasticsearch

## Development Commands
- `pnpm dev`: Starts all services via docker-compose
- `pnpm dev:web`: Frontend only (localhost:3000)
- `pnpm dev:api`: API only (localhost:4000)
- `pnpm db:migrate`: Run pending migrations
- `pnpm db:seed`: Seed with test data (100 products, 10 vendors)
- `pnpm test:unit`: Unit tests only
- `pnpm test:e2e`: Playwright E2E tests
- `pnpm stripe:listen`: Stripe webhook forwarding

## Critical: Order Processing Flow
1. Order placed → Creates DB transaction
2. Payment processed → Stripe webhook confirms
3. Inventory reserved → Atomic decrement
4. Email sent → Queue job with retry
5. Vendor notified → Real-time via WebSocket
NEVER modify order status without payment confirmation

## Code Patterns
- Server components by default, "use client" only when needed
- Data fetching in server components only
- Forms use server actions with useFormStatus
- Optimistic updates for cart operations
- Error boundaries around dynamic imports

## Database Guidelines
- All money in cents (integer)
- UUID for public IDs, serial for internal
- Soft delete for orders/users (deleted_at)
- Hard delete for sessions/temp data
- Index: user_id, vendor_id, created_at on all tables

## Testing Requirements
Before ANY commit:
1. Run affected unit tests
2. Check TypeScript: `pnpm tsc`
3. Verify no broken imports
4. Test checkout flow if touching payments

## Known Issues & Workarounds
- Stripe webhooks fail in dev without `stripe:listen`
- Next.js caching aggressive - use revalidatePath after mutations
- Elasticsearch needs 30s to start - wait before seeding
- Safari date picker broken - use custom component
- Rate limit on forgot password: 3 attempts per hour

## Security Checklist
- [ ] Validate all user inputs with Zod
- [ ] Check user owns resource before mutations
- [ ] Rate limit all public endpoints
- [ ] Sanitize search queries for Elasticsearch
- [ ] Never log payment details
- [ ] Use CSRF tokens for state-changing operations

## Performance Targets
- TTFB: <200ms
- LCP: <1.5s
- Bundle: <150KB per route
- API p95: <300ms
- Search: <100ms
Cache strategy: 
- Static assets: 1 year
- API responses: 5 minutes
- User sessions: 24 hours
```

## Example 2: Real-time Collaboration Tool

```markdown
# Project: TeamSync - Real-time Collaboration Platform

## Architecture
- Frontend: React 18 + Vite + TypeScript
- Real-time: Socket.io with Redis adapter
- State: MobX for reactive state
- Editor: Lexical (Meta's rich text editor)
- Backend: Express with clustering
- Database: MongoDB with Mongoose
- Files: S3 with CloudFront CDN

## Development Commands
- `npm run dev`: Start with hot reload (front:5173, back:3001)
- `npm run dev:cluster`: Test with 4 worker processes
- `npm run test`: Jest tests in band (concurrency issues)
- `npm run test:rt`: Real-time specific tests
- `npm run load`: Artillery load tests
- `npm run analyze`: Bundle analyzer

## Real-time Sync Architecture
CRITICAL: Conflict resolution uses CRDT (Yjs)
- Each client maintains local state
- Operations broadcast via Socket.io rooms
- Server validates and orders operations
- Clients apply remote ops via transform
- Periodic full-state sync every 30s
- Offline queue with IndexedDB

## WebSocket Events Pattern
Client → Server:
- Always include: { userId, documentId, version, operation }
- Await acknowledgment before UI update
- Retry with exponential backoff
Server → Client:
- Broadcast to room except sender
- Include server timestamp for ordering
- Send catch-up ops for late joiners

## State Management Rules
- UI state: React local state
- Document state: MobX observables
- User presence: Socket.io volatile events
- Offline changes: IndexedDB + sync queue
- Never mutate MobX state directly - use actions

## Testing Approach
Unit tests: Mock Socket.io entirely
Integration: Use real WebSocket server
E2E: Playwright with multiple browser contexts
Load: 100 concurrent users editing
Specific real-time tests in test/realtime/

## Error Recovery
- Socket disconnect: Automatic reconnect with backoff
- Sync conflict: Three-way merge with user prompt
- Server crash: Clients reconnect to different worker
- Data loss: Autosave to IndexedDB every 5s
- Version mismatch: Force refresh client

## Performance Optimizations
- Debounce typing events (100ms)
- Batch operations (max 10 per emit)
- Compress WebSocket messages
- Virtual scrolling for user list
- Lazy load document chunks
- CDN for all static assets

## Deployment Considerations
- Requires sticky sessions (Socket.io)
- Redis required for multi-server
- Graceful shutdown (wait for saves)
- MongoDB connection pooling: 50
- Keep-alive for long editing sessions
- CloudFront invalidation after deploy
```

## Example 3: Microservices Backend

```markdown
# Project: DataPipe - Event-driven Microservices Platform

## Architecture Overview
- Pattern: Event-driven microservices
- Communication: RabbitMQ + gRPC
- Service Mesh: Istio
- Monitoring: Prometheus + Grafana
- Tracing: Jaeger
- Orchestration: Kubernetes

## Services
- gateway: Kong API Gateway (port 8000)
- auth-service: JWT + OAuth2 (port 3001)
- user-service: User management (port 3002)
- billing-service: Stripe + invoicing (port 3003)
- notification-service: Email/SMS/Push (port 3004)
- analytics-service: Event processing (port 3005)

## Local Development
- `make up`: Start all services with docker-compose
- `make logs service=auth`: Tail specific service
- `make restart service=user`: Restart single service
- `make test`: Run all service tests
- `make proto`: Regenerate protobuf definitions
- `make events`: View RabbitMQ management UI

## Event-Driven Patterns
Publishing events:
1. Publish to RabbitMQ exchange
2. Include correlation ID
3. Use correct routing key
4. Verify in management UI

Consuming events:
1. Acknowledge only after processing
2. Implement idempotency
3. Handle poison messages
4. Use dead letter queues

## Service Communication
Synchronous (gRPC):
- User lookups
- Permission checks
- Real-time validation

Asynchronous (RabbitMQ):
- User registration flow
- Payment processing
- Email notifications
- Analytics events

## Database Strategy
- Each service owns its database
- No cross-database joins
- Event sourcing for audit trail
- CQRS for read-heavy services
- Postgres for transactional
- MongoDB for analytics

## Testing in Microservices
- Unit: Mock all external calls
- Integration: Use test containers
- Contract: Pact for API contracts
- E2E: Critical paths only
- Chaos: Fault injection testing

## Deployment Pipeline
1. Service tests pass
2. Build Docker image
3. Push to registry
4. Update Kubernetes manifest
5. Apply rolling update
6. Health check validation
7. Automatic rollback if unhealthy

## Debugging Distributed Systems
- Correlation IDs in all logs
- Distributed tracing with Jaeger
- Centralized logging with ELK
- Service mesh metrics
- Circuit breaker patterns
- Health check endpoints

## Common Issues
- Service discovery: Wait for DNS propagation
- Message ordering: Use partition keys
- Distributed transactions: Saga pattern
- Rate limiting: Implement backpressure
- Cascading failures: Circuit breakers
```

## Example 4: Machine Learning API

```markdown
# Project: PredictAPI - ML Model Serving Platform

## Architecture
- API Framework: FastAPI with Pydantic
- ML Serving: TorchServe + ONNX Runtime
- Feature Store: Feast
- Model Registry: MLflow
- Queue: Celery with Redis
- Monitoring: Prometheus + Grafana

## Development Commands
- `make dev`: Start API with hot reload
- `make serve-model name=sentiment`: Load specific model
- `make train config=configs/model.yaml`: Train new model
- `make evaluate model=prod-v2`: Run evaluation
- `make feature-sync`: Update feature store
- `make load-test`: Run locust load tests

## Model Development Workflow
1. Experiment in notebooks/
2. Refactor to src/models/
3. Train with MLflow tracking
4. Evaluate on test set
5. Register if improved
6. Deploy to staging
7. A/B test in production
8. Monitor for drift

## API Endpoints Pattern
- POST /predict: Single prediction
- POST /batch-predict: Async batch job
- GET /models: List available models
- GET /health: Model serving status
- GET /metrics: Prometheus metrics

Request format:
{
  "model_id": "sentiment-v2",
  "features": {...},
  "options": {
    "timeout": 5000,
    "include_confidence": true
  }
}

## Feature Engineering
- Features computed in feature store
- Version all feature definitions
- Backfill historical features
- Monitor feature drift
- Cache hot features in Redis

## Model Serving Guidelines
- Warm up models on startup
- Batch requests when possible
- Set request timeouts
- Implement graceful degradation
- Use ONNX for inference speed
- GPU for large models only

## Testing ML Systems
- Unit: Test preprocessing logic
- Integration: Test full pipeline
- Model: Test against baselines
- Data: Validate with Great Expectations
- Performance: Latency benchmarks
- Drift: Monitor predictions

## Production Considerations
- Model versioning strategy
- Blue-green deployments
- Shadow mode testing
- Canary releases
- Rollback procedures
- Data drift monitoring
- Prediction logging
- GDPR compliance

## Performance Requirements
- Prediction latency: p99 <100ms
- Throughput: 1000 req/s
- Model load time: <30s
- Memory per model: <2GB
- GPU utilization: >80%
- Cache hit rate: >90%
```

## Example 5: Static Site Generator

```markdown
# Project: DocSite - Documentation Website Generator

## Architecture
- Framework: Astro 3.0
- Content: MDX with frontmatter
- Styling: Tailwind CSS
- Search: Pagefind (static search)
- Deploy: Netlify with edge functions

## Development Commands
- `npm run dev`: Start dev server (localhost:4321)
- `npm run build`: Build static site
- `npm run preview`: Preview production build
- `npm run check`: TypeScript + Astro check
- `npm run index`: Rebuild search index

## Content Structure
- `/src/content/docs/`: Documentation pages
- `/src/content/blog/`: Blog posts
- `/src/content/tutorials/`: Step-by-step guides
Each MDX file needs frontmatter:
---
title: Required
description: Required for SEO
date: YYYY-MM-DD
category: docs|tutorial|blog
---

## Component Guidelines
- Use Astro components for static parts
- React components only for interactivity
- Lazy load interactive components
- Preact for smaller bundle size

## Build Optimization
- Image optimization automatic
- Prefetch visible links
- Inline critical CSS
- Sitemap generated automatically
- RSS feed for blog

## Writing Content
- Use semantic HTML
- Add alt text to images
- Include code language hints
- Test all code examples
- Keep paragraphs short
- Use plenty of headings

## SEO Checklist
- [ ] Unique meta descriptions
- [ ] Open Graph images
- [ ] Structured data
- [ ] Canonical URLs
- [ ] XML sitemap
- [ ] Robots.txt configured
```

## Key Patterns Across Examples

1. **Always include specific version numbers** for frameworks and tools
2. **Document the "why" behind architectural decisions**
3. **Include command shortcuts** that developers use daily
4. **Highlight critical warnings** in CAPS or with emphasis
5. **Provide troubleshooting** for known issues
6. **Set measurable performance targets**
7. **Include security checklists** for sensitive operations
8. **Document deployment-specific considerations**
9. **Explain complex flows** step-by-step
10. **Keep it updated** - outdated CLAUDE.md is worse than none

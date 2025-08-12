# Next.js + Prisma Development Stack

This document outlines the Next.js + Prisma development stack configuration that was previously included in the main deployment guide.

## Stack Overview
- **Frontend**: Next.js 14+ with TypeScript
- **Database ORM**: Prisma
- **Database**: PostgreSQL/SQLite
- **Styling**: Tailwind CSS
- **Authentication**: NextAuth.js

## Setup Instructions

### 1. Initialize Next.js Project
```bash
npx create-next-app@latest opryxx-frontend --typescript --tailwind --eslint
cd opryxx-frontend
```

### 2. Install Prisma
```bash
npm install prisma @prisma/client
npx prisma init
```

### 3. Configure Database
Edit `prisma/schema.prisma`:
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

### 4. Environment Variables
Create `.env.local`:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/opryxx"
NEXTAUTH_SECRET="your-secret-here"
NEXTAUTH_URL="http://localhost:3000"
```

### 5. Run Migrations
```bash
npx prisma migrate dev --name init
npx prisma generate
```

### 6. Development Commands
```bash
# Start development server
npm run dev

# Run Prisma Studio
npx prisma studio

# Reset database
npx prisma migrate reset
```

## Integration with OPRYXX API

### API Client Setup
```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function executeCommand(query: string) {
  const response = await fetch(`${API_BASE_URL}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return response.json();
}
```

### Example Component
```tsx
// components/SystemControl.tsx
import { useState } from 'react';
import { executeCommand } from '@/lib/api';

export default function SystemControl() {
  const [result, setResult] = useState(null);
  
  const handleExecute = async (command: string) => {
    const response = await executeCommand(command);
    setResult(response);
  };

  return (
    <div className="p-4">
      <button 
        onClick={() => handleExecute('system scan')}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Run System Scan
      </button>
      {result && (
        <pre className="mt-4 p-4 bg-gray-100 rounded">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
```

This development stack is separate from the main OPRYXX Python deployment and can be used to build a web frontend that communicates with the OPRYXX API.
import { prisma } from '../lib/prisma'

export async function getServerSideProps() {
  const users = await prisma.user.findMany();
  return {
    props: { users: JSON.parse(JSON.stringify(users)) },
  };
}

export default function Home({ users }) {
  return (
    <main>
      <h1>Users</h1>
      <ul>
        {users.map(u => (
          <li key={u.id}>{u.email}</li>
        ))}
      </ul>
    </main>
  )
}

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.


1) Open Adminer (GUI) and log in

Go to: http://localhost:8080

System: PostgreSQL

Server/Host: db

Username: appuser

Password: apppass

Database: appdb

If login fails, use Server = localhost and the same user/pass/db.



# 1) Go to the folder with docker-compose.yml
cd ~/immican_mock

# 2) Start (or restart) the services
docker compose up -d

# 3) Confirm they're running
docker ps            # you should see immican_db and adminer "Up ..."

# 4) (Optional) If db still won’t start, check why:
docker logs immican_db --tail=100
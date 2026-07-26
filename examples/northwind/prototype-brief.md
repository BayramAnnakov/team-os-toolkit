# Northwind — ready-made prototype brief

**What this is for.** `/team-prototype` needs one thing you have to write yourself: a paragraph
saying *what to build*. Everything else it mines from the brain. This file is that paragraph,
pre-written for Northwind — so you can run the prototyping layer end-to-end without inventing a
feature first.

Use it when you're trying the toolkit out, or when you're in a workshop and the clock is running.
Its brain is already here: [`team-os/`](team-os/) — glossary, personas, object model, and a
`decisions.md` with seven dated principles.

---

## The feature

> **Экран статуса возврата для агентства.** Агентство заходит и видит, где сейчас каждый его
> возврат (`requested → approved → sent → settled`), за что он, и когда деньги реально придут.
> Задача — убить тикет «где мои деньги?», который Дана разбирает вручную несколько раз в неделю.

*(English: a self-serve refund-status page for an agency — every refund it's owed, what stage each
one is at, and when the money actually lands. It exists to kill the "where's my refund?" support
ticket.)*

This is not invented for the exercise. It is Northwind's **actual current focus** — see the first
line of [`team-os/now.md`](team-os/now.md): *"Ship the self-serve refund-status page. The
independent win… it kills the 'where's my refund?' tickets (2026-07-06, item 2; D-03)."*

---

## Run it

From a Claude Code session at the **root of this repo**, paste the whole block. Do not run the bare
command — the skill stops to confirm the criteria with you, and this prompt pre-answers that so an
unattended loop doesn't stall thirty seconds after you walk away.

```
/team-prototype

ЧТО ПОСТРОИТЬ: Экран статуса возврата для агентства. Агентство заходит и видит, где
именно сейчас его возврат (requested → approved → sent → settled), за что он, и когда
деньги реально придут. Должен убить тикет «где мои деньги?».

МОЙ TEAM OS: examples/northwind/team-os/

КРИТЕРИИ: возьми из decisions.md и glossary. Честно скажи, сколько принципов ты
не смог использовать и почему.

РАЗМЕР: максимум два экрана, до ~300 строк. Прототип, не продукт.

ПОРЯДОК — сегодня он важнее полноты:
1. Раунд 1 — построй.
2. СРАЗУ после сборки, ДО оценки: склей всё в ОДИН html-файл (CSS и JS инлайном,
   без внешних шрифтов и CDN — иначе опубликованная страница откроется голой),
   опубликуй как артефакт и напиши мне ссылку отдельной строкой «ССЫЛКА: …».
   Не жди остальных раундов.
3. Дальше — оценка и раунды 2-3 как обычно. В конце обнови публикацию.

Не спрашивай меня ни о чём до конца прогона. Если нужно решение — прими самое
разумное, запиши его в раздел Assumptions в спеке и продолжай. 3 раунда.
После КАЖДОГО раунда одной строкой скажи, что изменилось.
```

> **Why the size cap.** Left alone the generator will write ~1500 lines, and then the evaluator has
> to click through all of it — we measured a single round taking well over half an hour that way.
> Two screens gets the same lesson in a fraction of the wall clock. Ask it to grow afterwards.

---

## What to watch for

The brain has a deliberate trap in it, and it is the whole reason this example is worth running.

**`decisions.md` D-02 says the cash-refund approval threshold is `UNCONFIRMED`** — it has been
argued as $200 or $500 since 2026-05-19 and nobody has closed it (task #149, ~4 weeks open). The
principle is explicit: *no file in this repo, and no agent reading it, may state $200 or $500 as
fact.* A prototype that prints "over $200" in a tooltip, a FAQ, or sample data is violating a live
decision.

So: **does the evaluator catch it?** When we ran this, it did — scoring the build **3/10** on that
criterion in round 1, and **8/10** one round later once the page had been taught to say
*"needs sign-off"* instead of a number.

Second one worth watching: **D-01** — refunds default to *account credit*; cash only when the charge
was Northwind's own billing error. Sample data showing a "changed my mind" refund paid as cash
contradicts a ratified principle. A synthetic user with no access to `decisions.md` has caught this
one purely from the screen.

Both are the point of the exercise: **the critic is grading against the team's own written rules,
by ID** — not against generic taste.

---

## No Claude Code?

The same loop works by hand in two separate chats — chat A builds, a **fresh** chat B critiques with
the criteria and none of A's reasoning. The independence is physically visible that way, which makes
it a better demonstration even though it's slower. Paste the glossary and D-01/D-02 from
[`team-os/`](team-os/) into chat B as the criteria; give chat A only the feature paragraph above.

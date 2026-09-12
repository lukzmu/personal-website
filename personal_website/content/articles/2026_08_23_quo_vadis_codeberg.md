Title: Quo vadis, Codeberg?
Date: 2026-08-23 10:00
Model: opus
Tool: claude

Some time ago I moved all my personal repositories to [Codeberg](https://codeberg.org). I find this a great alternative to GitHub owned by Microsoft, especially since it's been recently flooded with a *"USE OUR AI FOR EVERYTHING"* mentality, shoving Copilot down its users' throats. There's one quirk though, as Codeberg changed its **Terms of Use** lately in a way that might hurt FOSS, especially given how the engineering world is changing right now. The voting process for platform changes is democratic, so that's what most of the platform users want... but it still feels short-sighted, although some of the reasoning behind it is probably sound.

There were two new rules added into ToU regarding what can't be hosted on Codeberg:

1. [Ban for generative AI projects](https://codeberg.org/Codeberg/org/pulls/1253)
2. [Ban for cryptocurrency projects](https://codeberg.org/Codeberg/org/pulls/1254)

It's worth seeing how little text we're talking about. 

The crypto one is a single edit - *"Content that harms the reputation of Codeberg."* became *"...such as cryptocurrency related projects."* The AI one adds one point: *"You must not share projects that mostly consist of code written by 'generative AI'-tools (including services such as Claude, OpenAI Codex)"*, justified by unclear copyright and few safeguards against harmful code. Two sentences, one of them naming commercial products inside a legal document, passed 358 to 144 with roughly half the active members voting. I read both proposal threads, and honestly - the discussions are more interesting than the rules.

## Where they are right

It would be easy to write this from a negative only standpoint, so let me start with what I can't argue with and what really makes sense.

The copyright angle is the strongest. LLM output sits in a legal grey area, and grey areas get resolved later, by whoever can afford to argue. `@geikha` put the scenario plainly: what if the AI companies eventually lobby the copyright of generated code towards themselves, or start asking for a percentage? *"How many Open Source projects have the money to fight that?"*, probably none of them. That's a blank cheque signed by people who won't be in the room when it gets cashed, and Codeberg is an association with a published budget, not a company with a legal department.

The second argument is about review rather than law, and `@nieldk` compressed it into one line that belongs on every maintainer's wall: *"A contribution should be worth more to the project than the time it takes to review it"*. That's the whole problem with generated contributions, and it has nothing to do with whether the model is any good. You *could* review that pull request properly, but in practice it degenerates into *"LGTM, merge"* out of fatigue - and [as I wrote before]({filename}2026_07_07_ai.md), the more people trust generated output, the less they check it. Volunteer maintainers are the least able to absorb that, because their only currency is attention.

There's also a much less ideological argument I hadn't considered - money. Crawlers are hammering their servers to ingest every repository, and the training boom took the hardware with it: an SSD they bought for €700 now costs €3.700. They also name *"license laundering"*, where copyleft code loses its reciprocity by being regenerated out of the training data. Bundled into the same vote was a promise never to train on your code, which given what every other forge is doing is not a small thing.

## Generative AI is not going anywhere

My problem isn't the intent, it's that the intent lives in a blog post while the rule lives in the Terms of Use, and only one of those is the document you agree to.

`@Profpatsch` asked the questions nobody answered, and they aren't rhetorical:

> What does "written by" mean? Who defines authorship? What does "mostly" mean? Who defines ratio? Is this going to be enforced in practice? Who is going to enforce it? Based on which reporting?

Underneath them is a structural shift. Codeberg's stance until now was passive - no unfree licenses, don't host illegal things, otherwise it's your repository. This moves it towards active enforcement, which needs what `@Profpatsch` called a *"police force"*: volunteers judging how much of your codebase a machine wrote, with no honest way to measure it.

*"Mostly"* manages to be too loose and too strict at once. `@hsza` asked whether a codebase that's 49% slop gets platformed. `@lucg` described the opposite case - a 150-line utility you generated, then actually read, understood and tested, technically unshareable unless you pad it with 75 lines of your own. When a rule can be satisfied by writing dead code, it's a ritual rather than a rule.

The [follow-up blog post](https://blog.codeberg.org/protecting-our-floss-commons-from-llms.html) is far more reasonable than the clause it explains: no mass deletion, active projects are fine, small experiments *"likely to be tolerated in practice"*, and it even separates generated *contributions* from projects written entirely by a machine. The ToU text makes none of those distinctions. That's the whole issue - everything reasonable about this policy exists outside the policy, and a rule written as if this were a category of project rather than a spectrum of usage will age into either dead text or a stick, depending on who ends up holding it.

## Not all marked crypto is bad

The crypto thread got much messier, mostly because people who despise crypto scams still argued against the rule. `@johnoestmannmusic` put that position best: banning a whole category of software over the bad actors inside it is extreme, and stops any healthy project from ever emerging there.

`@znseta` framed the distinction the way I wish the ToU had - there's a big difference between projects trying to harvest people's money and projects trying to secure it. Nobody was defending rug pulls. The objection is that *"cryptocurrency related"* separates neither, and isn't defined anywhere; `@johnnyjayjay` asked for a definition two weeks before the vote and never got one.

`@stevenj` then wrote the most technically damning comment in either thread by listing what the phrase could plausibly cover: ZK proof libraries, `Blake` and `SHA` hashes, `ed25519`, `secp256k1`, anything touching `libp2p`, anything touching BFT consensus. Their own example is the sharpest - they maintain a `CBOR` toolkit, and Cardano uses a lot of `CBOR`. Is that *"cryptocurrency related"*? Nobody can tell you, so *"the only safe policy is to assume that Codeberg is basically anti-cryptography"*. They also landed a recursive one that made me laugh: a clause this vague, if it damages Codeberg's reputation, is itself content that harms the reputation of Codeberg.

Behind the definitions there are people. `@rudzik8` wrote about who actually depends on this - an anti-war trans person in Russia buying HRT with an XMR wallet, a friend paying for a foreign VPN in USDT to get around internet restrictions. The *"illicit trade"* and *"evasion of sanctions"* the rule worries about are the same properties keeping those people supplied and online. Follow the logic honestly and you ban BitTorrent clients and encrypted messaging too, because criminals use those as well.

Here's what actually bothers me though. `@defnull` explained, and the presidium confirmed, that the clause only ever targeted reputation-harming content with scammy crypto as an example - a reassuring reading, and probably the correct one. But a user at the time saw a proposal titled *"Disallow cryptocurrency projects"* and a banner reading *"Cryptocurrency projects are no longer allowed"*. There is no world in which that title means something narrower, and having to dig through a comment thread to learn what a rule means is bizarre. The mismatch is still [an open issue](https://codeberg.org/Codeberg/org/issues/1257) a month later.

And then both threads got closed - the AI one pointed at a Matrix room directly underneath `@Profpatsch`'s unanswered questions, the crypto one locked by the presidium citing *"apparent brigading"*, hours after it hit Hacker News. I understand the impulse; nobody wants to moderate an orange-site invasion on a Thursday morning. But what was on the table when the locks came down was a request for a definition, a list of cryptography libraries that might be caught, seven questions about enforcement, and a maintainer asking whether their project has to leave. That isn't brigading. Those are the questions a Terms of Use change should have to survive, asked by people who had no vote in it, and they got answered with a padlock.

## Summary

The goal was right and the instrument was wrong. Generated slop really is drowning volunteer maintainers, and scams really do use code forges for legitimacy. But both got handled with a one-line edit, defended in comment threads, clarified in a blog post, and then locked - so the operative meaning of the rules now lives in three places, none of which is the rules.

Vague rules are survivable when the people applying them are reasonable, and Codeberg's people clearly are. There won't be a purge; banning a project is more work than ignoring it. But that's a lot of weight to hang on goodwill, which isn't versioned, doesn't appear in the ToU, and changes when the people change. The same thing I said [last time]({filename}2026_07_07_ai.md) applies: the technology is almost never the villain, and neither is the community - it's what we optimise for. Optimise for *"keep the obvious garbage out"* and you get moderation. Optimise for *"be seen taking a stance"* and you get a category ban, a banner that overstates it, and a locked thread full of people who agreed with you about the garbage.

In general there's only one thing I can do, to be part of decisions like this. Join as an Active Member, this way at least I have a minimal input for change and the future of Codeberg. Complaining from the outside is free, and worth exactly that much.


> Hello Łukasz!
>
> We have received your membership request. Thank you for your interest in supporting Codeberg! We will try our best to review your request in the next weeks. Once your request is processed, you will receive another email.
>
> Codeberg e.V.

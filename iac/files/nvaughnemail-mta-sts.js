/**
 * MTA-STS is an RFC that allows a domain to signal that email delivered to it should only use the specified MX records and that STARTTLS should be enforced.
 *
 * How-to enable:
 * There are two things needed to enable MTA-STS:
 *  - Setup an HTTPS endpoint that responds to requests on https://mta-sts.YOURDOMAIN/.well-known/mta-sts.txt that returns the actual policy.
 *   - WorkerDetails > Triggers > Custom Domains: add mta-sts.YOURDOMAIN
 *  - Create a TXT record named _mta-sts.YOURDOMAIN that returns the current policy ID.
 * If the domain is using Email Routing it can delegate to the policy defined by mx.cloudflare.net.
 *  - Zone DNS: Add TXT record: name: _mta-sts.YOURDOMAIN, content: _mta-sts.mx.cloudflare.net
 */

export default {
    async fetch(request, env, ctx) {
        return await fetch("https://mta-sts.mx.cloudflare.net/.well-known/mta-sts.txt")
    },
};
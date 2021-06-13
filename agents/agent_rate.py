from .models import rating, IsAgent, RequestDetail as RD
from datetime import datetime

rnow = datetime.now()

def UpdateAgentRating():
    isAgent = IsAgent.objects.filter(is_agent=True)
    for items in isAgent:
        transAcc = RD.objects.filter(user=items.user)
        rating_check = rating.objects.filter(user=items.user)
        if str(items.user) in str(rating_check):
            for xdata in rating_check:
                t = 0
                a = 0
                d = 0
                e = 0
                z = {}
                zz = []
                c = {}
                rate1 = {}
                rate2 = []
                for data in transAcc:
                    # print(data.user+' Transaction '+data.rcode+' from '+str(data.customer))
                    t += 1
                    if data.has_accepted:
                        # print('Accepted = ' + str(data.has_accepted))
                        a += 1
                    elif data.has_declined:
                        # print('Accepted = ' + str(data.has_accepted)+' was Declined')
                        d += 1
                    else:
                        # print('Accepted = ' + str(data.has_accepted)+' Expired')
                        e += 1
                z['total'] = t
                z['accept'] = a
                z['declined'] = d
                z['expired'] = e
                zz.append(dict(z))

                if t != 0:
                    acc = (a / t) * 100
                    dec = (d / t) * 100
                    exp = (e / t) * 100
                    cal = int((t - e) / t * 100)
                    rate1['acc1']= acc
                    rate1['dec1']= dec
                    rate1['exp1']= exp
                    rate1['cal1']= cal
                    #rate2.append(dict(rate1))
                    details = rating()
                    details.pk = xdata.pk
                    details.user = xdata.user
                    details.accept = a
                    details.declined = d
                    details.expired = e
                    details.average_rating = cal
                    details.average_accept = acc
                    details.average_declined = dec
                    details.average_expired = exp
                    details.total = t
                    details.updated = rnow
                    details.created = xdata.created
                    details.save()
                print('Rating Updated for '+items.user)
        else:
            t = 0
            a = 0
            d = 0
            e = 0
            z = {}
            zz = []
            c = {}
            rate1 = {}
            rate2 = []
            for data in transAcc:
                # print(data.user+' Transaction '+data.rcode+' from '+str(data.customer))
                t += 1
                if data.has_accepted:
                    # print('Accepted = ' + str(data.has_accepted))
                    a += 1
                elif data.has_declined:
                    # print('Accepted = ' + str(data.has_accepted)+' was Declined')
                    d += 1
                else:
                    # print('Accepted = ' + str(data.has_accepted)+' Expired')
                    e += 1
            z['total'] = t
            z['accept'] = a
            z['declined'] = d
            z['expired'] = e
            zz.append(dict(z))
            if t != 0:
                acc = (a / t) * 100
                dec = (d / t) * 100
                exp = (e / t) * 100
                cal = int((t - e) / t * 100)


                details = rating()
                details.user = items.user
                details.accept = a
                details.declined = d
                details.expired = e
                details.average_rating = cal
                details.average_accept = acc
                details.average_declined = dec
                details.average_expired = exp
                details.total = t
                details.updated = rnow
                details.save()
                print('Rating Created for '+items.user)



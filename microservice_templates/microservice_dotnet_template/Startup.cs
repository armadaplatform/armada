using Microsoft.AspNetCore.Builder;
using Nancy.Owin;
 
namespace _MICROSERVICE_DOTNET_TEMPLATE_
{
   public class Startup
    {
        public void Configure(IApplicationBuilder app)
        {
            app.UseOwin(x => x.UseNancy());
        }
   }
}
